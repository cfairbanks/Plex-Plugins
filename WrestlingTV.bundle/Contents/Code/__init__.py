import GoogleSearcher
import SeriesUpdater
import TVRageSearcher
import WrestlingConstants


def Start():
    HTTP.CacheTime = CACHE_1DAY


def ValidatePrefs():
    Log("validateprefs")


class WrestlingTVAgent(Agent.TV_Shows):
    name = 'WrestlingTV'
    languages = [Locale.Language.English]
    primary_provider = True

    def search(self, results, media, lang, manual=False):
        Log("search: START")

        if Prefs["clear_cache"]:
            Log("clearing http cache")
            HTTP.ClearCache()

        variations = WrestlingConstants.get_show_name_variations(media.show)

        TVRageSearcher.Searcher(results=results,
                                show_names=variations,
                                year=media.year,
                                lang=lang,
                                force_refresh=manual).search()

        GoogleSearcher.Searcher(results=results,
                                media=media,
                                lang=lang,
                                force_refresh=manual).search()

        remove_duplicate_results(results)

        Log("search: END")

    def update(self, metadata, media, lang, force=False):
        Log("update: START")

        if Prefs["clear_cache"]:
            Log("clearing http cache")
            HTTP.ClearCache()

        SeriesUpdater.Updater(metadata=metadata,
                              media=media,
                              lang=lang,
                              tvdb_id=WrestlingConstants.convert_tvrage_to_tvdb(metadata.id),
                              force_refresh=force).update()

        Log("update: END")


def remove_duplicate_results(results):
    """
    Removes results with duplicate result IDs, making sure to keep the highest score for the id
    """
    if len(results) > 0:
        results.Sort('score', descending=True)

        to_remove = []
        result_map = {}

        for result in results:
            if not result_map.has_key(result.id):
                result_map[result.id] = True
            else:
                to_remove.append(result)

        for dupe in to_remove:
            results.Remove(dupe)
