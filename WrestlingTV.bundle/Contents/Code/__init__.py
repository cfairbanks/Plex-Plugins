from urllib2 import URLError
import TVRageNetwork, ImageUpdater

TVRAGE_API_KEY = 'P8q4BaUCuRJPYWys3RBV'
# TVRAGE_API_KEY = 'bX9ymM850oC0KCZ88YZn'
TVRAGE_SEARCH_URL = 'http://services.tvrage.com/myfeeds/search.php?key=%s&show=%%s' % TVRAGE_API_KEY
TVRAGE_SHOW_INFO_URL = 'http://services.tvrage.com/myfeeds/showinfo.php?key=%s&sid=%%s' % TVRAGE_API_KEY
TVRAGE_EPISODE_LIST_URL = 'http://services.tvrage.com/myfeeds/episode_list.php?key=%s&sid=%%s' % TVRAGE_API_KEY


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

        if Prefs["clearcache"]:
            Log("clearing http cache")
            HTTP.ClearCache()

        Log("search show input: " + media.show)

        if media.show.isdigit():
            info_url = TVRAGE_SHOW_INFO_URL % String.Quote(media.show, True)
            info_xml = TVRageNetwork.fetchXML(info_url)
            if info_xml:
                nextResult = MetadataSearchResult(id=str(info_xml.xpath("/Showinfo/showid")[0].text),
                                                  name=str(info_xml.xpath("/Showinfo/showname")[0].text),
                                                  year=info_xml.xpath("/Showinfo/started")[0].text,
                                                  score=100,
                                                  lang=lang)
                results.Append(nextResult)
                Log(repr(nextResult))

        search_url = TVRAGE_SEARCH_URL % String.Quote(media.show, True)
        search_xml = TVRageNetwork.fetchXML(search_url)
        curscore = 49

        show_name_from_server = search_xml.xpath("//show/name")[0].text if search_xml.xpath("//show/name") else ''

        if media.show.lower().replace('-', ' ') == show_name_from_server.lower().replace('-', ' '):
            curscore = 100
        for match in search_xml.xpath("//show"):
            nextResult = MetadataSearchResult(id=str(match.xpath("./showid")[0].text),
                                              name=str(match.xpath("./name")[0].text),
                                              year=match.xpath("./started")[0].text,
                                              score=curscore,
                                              lang=lang)
            results.Append(nextResult)
            Log(repr(nextResult))
            curscore = curscore - 1
        Log("search: END")

    def update(self, metadata, media, lang):
        Log("update: START")
        Log(metadata.id)

        if Prefs["clearcache"]:
            Log("clearing http cache")
            HTTP.ClearCache()

        try:
            xml = TVRageNetwork.fetchXML(TVRAGE_SHOW_INFO_URL % metadata.id)
        except URLError as e:
            Log(e)
            Log("update: ERROR")
            return None

        metadata.title = xml.xpath("/Showinfo/showname")[0].text
        if xml.xpath("/Showinfo/network"):
            metadata.studio = xml.xpath("/Showinfo/network")[0].text
        metadata.duration = int(xml.xpath("/Showinfo/runtime")[0].text) * 60 * 1000
        metadata.originally_available_at = Datetime.ParseDate(xml.xpath("/Showinfo/started")[0].text).date()
        metadata.genres = [genre.text for genre in xml.xpath("/Showinfo/genres/genre")]
        if xml.xpath("/Showinfo/summary"):
            metadata.summary = xml.xpath("/Showinfo/summary")[0].text
        metadata.countries = [xml.xpath("/Showinfo/origin_country")[0].text]
        metadata.tags = [xml.xpath("/Showinfo/classification")[0].text]
        self.update_seasons(metadata.id, metadata.seasons, media.seasons)

        image_updater = ImageUpdater.Updater(metadata)
        image_updater.update_images(media.seasons)
        Log("update: END")

    def update_seasons(self, tvrage_id, metadata_seasons, season_numbers):
        Log("update_seasons: START")
        xml = TVRageNetwork.fetchXML(TVRAGE_EPISODE_LIST_URL % tvrage_id)

        if xml:
            for season in xml.xpath("/Show/Episodelist/Season"):
                season_number = season.get("no")
                if season_number in season_numbers:
                    Log("Season matched: " + season_number)
                    for episode in season.xpath("./episode"):
                        episode_number = str(int(episode.xpath("./seasonnum")[0].text))
                        if episode_number in season_numbers[season_number].episodes:
                            Log("Episode matched: " + episode_number)
                            ep_object = metadata_seasons[season_number].episodes[episode_number]
                            ep_object.title = episode.xpath("./title")[0].text
                            if episode.xpath("./summary"):
                                ep_object.summary = episode.xpath("./summary")[0].text
                            try:
                                Log("Date: " + str(Datetime.ParseDate(episode.xpath("./airdate")[0].text).date()))
                                ep_object.originally_available_at = Datetime.ParseDate(
                                    episode.xpath("./airdate")[0].text).date()
                            except ValueError as e:
                                Log(e)
                            Log("Abs: " + str(int(episode.xpath("./epnum")[0].text)))
                            ep_object.absolute_index = int(episode.xpath("./epnum")[0].text)
                            if len(episode.xpath("./screencap")) > 0:
                                thumb_url = episode.xpath("./screencap")[0].text
                                if thumb_url not in ep_object.thumbs:
                                    ep_object.thumbs[thumb_url] = Proxy.Media(HTTP.Request(thumb_url))
        Log("update_seasons: END")
