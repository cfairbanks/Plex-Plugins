import SeriesUpdater
import Searcher


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

        searcher = Searcher.Searcher(results, media, lang, manual)
        searcher.search()

        Log("search: END")

    def update(self, metadata, media, lang):
        if Prefs["clear_cache"]:
            Log("clearing http cache")
            HTTP.ClearCache()

        updater = SeriesUpdater.Updater(metadata, media, lang)
        updater.update()
