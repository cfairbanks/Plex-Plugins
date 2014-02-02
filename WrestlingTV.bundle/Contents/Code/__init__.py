TVRAGE_API_KEY = 'bX9ymM850oC0KCZ88YZn'
TVRAGE_SEARCH_URL = 'http://services.tvrage.com/feeds/search.php?key=%s&show=%%s' % TVRAGE_API_KEY
TVRAGE_SHOW_INFO_URL = 'http://services.tvrage.com/feeds/showinfo.php?key=%s&sid=%%s' % TVRAGE_API_KEY
TVRAGE_EPISODE_LIST_URL = 'http://services.tvrage.com/feeds/episode_list.php?key=%s&sid=%%s' % TVRAGE_API_KEY

TVDB_API_KEY = '607FE3FE16EDB11F'
TVDB_BANNER_LIST_URL = 'http://thetvdb.com/api/%s/series/%%s/banners.xml' % TVDB_API_KEY
TVDB_BANNER_BASE_URL = 'http://thetvdb.com/banners/'

ECW_HARDCORE_TV_TVRAGE = '1598'
ECW_HARDCORE_TV_TVDB = '76781'
ECW_ON_SCIFI_TVRAGE = '12105'
ECW_ON_SCIFI_TVDB = '79859'
ECW_ON_TNN_TVRAGE = '1597'
ECW_ON_TNN_TVDB = '76780'
ECW_PPV_TVRAGE = '1413'
ECW_PPV_TVDB = '73512'

TNA_IMPACT_TVRAGE = '6368'
TNA_IMPACT_TVDB = '264684'
TNA_PPV_TVRAGE = '548'
TNA_PPV_TVDB = ''

WCW_NITRO_TVRAGE = '6547'
WCW_NITRO_TVDB = '76962'
WCW_THUNDER_TVRAGE = '6550'
WCW_THUNDER_TVDB = '76782'
WCW_WORLDWIDE_TVRAGE = '685'
WCW_WORLDWIDE_TVDB = '71091'
WCW_PPV_TVRAGE = '6548'
WCW_PPV_TVDB = '276391'

WWE_HEAT_TVRAGE = '5392'
WWE_HEAT_TVDB = '72174'
WWE_NXT_TVRAGE = '25100'
WWE_NXT_TVDB = '144541'
WWE_PPV_TVRAGE = '6652'
WWE_PPV_TVDB = '70353'
WWE_RAW_TVRAGE = '6659'
WWE_RAW_TVDB = '76779'
WWE_SHOTGUN_TVRAGE = '6661'
WWE_SHOTGUN_TVDB = ''
WWE_SMACKDOWN_TVRAGE = '6655'
WWE_SMACKDOWN_TVDB = '75640'
WWE_TOTAL_DIVAS_TVRAGE = '35554'
WWE_TOTAL_DIVAS_TVDB = '271525'
WWE_TOUGH_ENOUGH_TVRAGE = '6656'
WWE_TOUGH_ENOUGH_TVDB = '76775'

TVDB_DICTIONARY = {
    ECW_HARDCORE_TV_TVRAGE: ECW_HARDCORE_TV_TVDB,
    ECW_ON_SCIFI_TVRAGE: ECW_ON_SCIFI_TVDB,
    ECW_ON_TNN_TVRAGE: ECW_ON_TNN_TVDB,
    ECW_PPV_TVRAGE: ECW_PPV_TVDB,

    TNA_IMPACT_TVRAGE: TNA_IMPACT_TVDB,
    TNA_PPV_TVRAGE: TNA_PPV_TVDB,

    WCW_NITRO_TVRAGE: WCW_NITRO_TVDB,
    WCW_THUNDER_TVRAGE: WCW_THUNDER_TVDB,
    WCW_WORLDWIDE_TVRAGE: WCW_WORLDWIDE_TVDB,
    WCW_PPV_TVRAGE: WCW_PPV_TVDB,

    WWE_HEAT_TVRAGE: WWE_HEAT_TVDB,
    WWE_NXT_TVRAGE: WWE_NXT_TVDB,
    WWE_PPV_TVRAGE: WWE_PPV_TVDB,
    WWE_RAW_TVRAGE: WWE_RAW_TVDB,
    WWE_SHOTGUN_TVRAGE: WWE_SHOTGUN_TVDB,
    WWE_SMACKDOWN_TVRAGE: WWE_SMACKDOWN_TVDB,
    WWE_TOTAL_DIVAS_TVRAGE: WWE_TOTAL_DIVAS_TVDB,
    WWE_TOUGH_ENOUGH_TVRAGE: WWE_TOUGH_ENOUGH_TVDB,
}


def Start():
    HTTP.CacheTime = CACHE_1DAY


class WrestlingTVAgent(Agent.TV_Shows):
    name = 'WrestlingTV'
    languages = [Locale.Language.English]
    primary_provider = True

    def search(self, results, media, lang):
        Log("search: START")
        if Prefs["clearcache"]:
            HTTP.ClearCache()
        Log("search show input: " + media.show)
        if media.show.isdigit():
            info_url = TVRAGE_SHOW_INFO_URL % String.Quote(media.show, True)
            Log("Searching using URL: " + info_url)
            info_xml = XML.ElementFromURL(info_url)
            nextResult = MetadataSearchResult(id=str(info_xml.xpath("/Showinfo/showid")[0].text),
                                              name=str(info_xml.xpath("/Showinfo/showname")[0].text),
                                              year=info_xml.xpath("/Showinfo/started")[0].text,
                                              score=100,
                                              lang=lang)
            results.Append(nextResult)
            Log(repr(nextResult))

        search_url = TVRAGE_SEARCH_URL % String.Quote(media.show, True)
        Log("Searching using URL: " + search_url)
        search_xml = XML.ElementFromURL(search_url)
        curscore = 49
        if media.show.lower().replace('-', ' ') == search_xml.xpath("//show/name")[0].text.lower().replace('-', ' '):
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

    def get_tvdb_id(self, tvrage_id):
        if tvrage_id in TVDB_DICTIONARY:
            return TVDB_DICTIONARY[tvrage_id]
        else:
            return None

    def update(self, metadata, media, lang):
        Log("update: START")
        Log(metadata.id)
        if Prefs["clearcache"]:
            HTTP.ClearCache()
        try:
            xml = XML.ElementFromURL(TVRAGE_SHOW_INFO_URL % metadata.id)
        except URLError as e:
            Log(e)
            Log("update: ERROR")
            return
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
        self.update_images(metadata.id, metadata)
        self.update_seasons(metadata.id, metadata.seasons, media.seasons)
        self.update_season_banners(metadata.id, metadata.seasons, media.seasons)
        Log("update: END")

    def update_images(self, tvrage_id, metadata):
        Log("update_images: START")
        for banner_xml in self.fetch_banner_data(tvrage_id):
            banner_type = self.get_banner_type(banner_xml)
            if banner_type == "fanart":
                self.update_from_fanart(metadata, banner_xml)
            elif banner_type == "poster":
                self.update_from_poster(metadata, banner_xml)
            elif banner_type == "series":
                self.update_from_series(metadata, banner_xml)
        Log("update_images: END")

    def update_from_fanart(self, metadata, banner_xml):
        banner_url = self.get_banner_url(banner_xml)
        if banner_url not in metadata.art:
            Log("Banner id: " + banner_xml.xpath("./id")[0].text)
            banner_sort = self.get_banner_sort(banner_xml)
            try:
                banner_thumb = TVDB_BANNER_BASE_URL + banner_xml.xpath("./ThumbnailPath")[0].text
                metadata.art[banner_url] = Proxy.Preview(HTTP.Request(banner_thumb), banner_sort)
            except:
                metadata.art[banner_url] = Proxy.Media(HTTP.Request(banner_url), banner_sort)

    def update_from_poster(self, metadata, banner_xml):
        banner_url = self.get_banner_url(banner_xml)
        if banner_url not in metadata.posters:
            Log("Banner id: " + banner_xml.xpath("./id")[0].text)
            banner_sort = self.get_banner_sort(banner_xml)
            try:
                banner_thumb = TVDB_BANNER_BASE_URL + banner_xml.xpath("./ThumbnailPath")[0].text
                metadata.posters[banner_url] = Proxy.Preview(HTTP.Request(banner_thumb), banner_sort)
            except:
                metadata.posters[banner_url] = Proxy.Media(HTTP.Request(banner_url), banner_sort)

    def update_from_series(self, metadata, banner_xml):
        banner_url = self.get_banner_url(banner_xml)
        if banner_url not in metadata.banners:
            Log("Banner id: " + banner_xml.xpath("./id")[0].text)
            banner_sort = self.get_banner_sort(banner_xml)
            metadata.banners[banner_url] = Proxy.Media(HTTP.Request(banner_url), banner_sort)

    def update_from_season(self, metadata_seasons, season_numbers, banner_xml):
        banner_url = self.get_banner_url(banner_xml)
        banner_season = banner_xml.xpath("./Season")[0].text
        if banner_season in season_numbers:
            Log("Banner id: " + banner_xml.xpath("./id")[0].text)
            banner_sort = self.get_banner_sort(banner_xml)
            if banner_xml.xpath("./BannerType2")[0].text == "season":
                if banner_url not in metadata_seasons[banner_season].posters:
                    metadata_seasons[banner_season].posters[banner_url] == Proxy.Media(HTTP.Request(banner_url),
                                                                                       banner_sort)
            elif banner_xml.xpath("./BannerType2")[0].text == "seasonwide":
                if banner_url not in metadata_seasons[banner_season].banners:
                    metadata_seasons[banner_season].banners[banner_url] == Proxy.Media(HTTP.request(banner_url),
                                                                                       banner_sort)

    def fetch_banner_data(self, tvrage_id):
        tvdb_id = self.get_tvdb_id(tvrage_id)
        if len(tvdb_id) > 0:
            Log("Banner url: " + TVDB_BANNER_LIST_URL % tvdb_id)
            xml = XML.ElementFromURL(TVDB_BANNER_LIST_URL % tvdb_id)
            return xml.xpath("/Banners/Banner")
        else:
            return []

    def get_banner_url(self, banner_xml):
        return TVDB_BANNER_BASE_URL + banner_xml.xpath("./BannerPath")[0].text

    def get_banner_sort(self, banner_xml):
        if banner_xml.xpath("./Rating")[0].text is not None:
            return int(10 - float(banner_xml.xpath("./Rating")[0].text))
        else:
            return None

    def get_banner_type(self, banner_xml):
        return banner_xml.xpath("./BannerType")[0].text

    def update_season_banners(self, tvrage_id, metadata_seasons, season_numbers):
        Log("update_season_banners: START")
        for banner_xml in self.fetch_banner_data(tvrage_id):
            banner_type = self.get_banner_type(banner_xml)
            if banner_type == "season":
                self.update_from_season(metadata_seasons, season_numbers, banner_xml)
        Log("update_season_banners: END")

    def update_seasons(self, tvrage_id, metadata_seasons, season_numbers):
        Log("update_seasons: START")
        xml = XML.ElementFromURL(TVRAGE_EPISODE_LIST_URL % tvrage_id)
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
