import GoogleSearcher
import SeriesUpdater
import TVRageSearcher


def Start():
    HTTP.CacheTime = CACHE_1DAY


def ValidatePrefs():
    Log("validateprefs")


class WrestlingTVAgent(Agent.TV_Shows):
    name = 'WrestlingTV'
    languages = [Locale.Language.English]
    primary_provider = True

    def search(self, results, media, lang, force_refresh=False):
        Log("search: START")

        if Prefs["clear_cache"]:
            Log("clearing http cache")
            HTTP.ClearCache()

        TVRageSearcher.Searcher(results=results, media=media, lang=lang, force_refresh=force_refresh).search()
        GoogleSearcher.Searcher(results=results, media=media, lang=lang, force_refresh=force_refresh).search()
        remove_duplicate_results(results)

        Log("search: END")

    def update(self, metadata, media, lang, force_refresh=False):
        Log("update: START")

        if Prefs["clear_cache"]:
            Log("clearing http cache")
            HTTP.ClearCache()

        SeriesUpdater.Updater(metadata=metadata, media=media, lang=lang, force_refresh=force_refresh).update()

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
