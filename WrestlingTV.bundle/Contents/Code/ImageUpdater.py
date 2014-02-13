import TVRageNetwork

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

ROH_WRESTLING_TVRAGE = '29472'
ROH_WRESTLING_TVDB = '266806'

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

    ROH_WRESTLING_TVRAGE: ROH_WRESTLING_TVDB,

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


class Updater():
    def __init__(self, metadata):
        self.tvrage_id = metadata.id
        self.tvdb_id = self.get_tvdb_id()
        self.art = metadata.art
        self.banners = metadata.banners
        self.posters = metadata.posters
        self.seasons = metadata.seasons

    def update_images(self, season_numbers):
        Log("update_images: START")

        data = self.fetch_banner_data()

        i = 0
        for xml in data:
            image = TVDBImage(xml)
            banner_type = image.get_type()
            if banner_type == "fanart":
                i += 1
                self.update_art(image, i)

        i = 0
        for xml in data:
            image = TVDBImage(xml)
            banner_type = image.get_type()
            if banner_type == "series":
                i += 1
                self.update_banners(image, i)

        i = 0
        for xml in data:
            image = TVDBImage(xml)
            banner_type = image.get_type()
            if banner_type == "season":
                i += 1
                self.update_seasons(image, season_numbers, i)

        i = 0
        for xml in data:
            i += 1
            image = TVDBImage(xml)
            banner_type = image.get_type()
            if banner_type == "poster":
                self.update_posters(image, i)
                self.update_posters_for_seasons(image, season_numbers)

        Log("update_images: END")

    def update_art(self, image, i):
        banner_url = image.get_url()
        if banner_url not in self.art:
            thumbnail = image.get_thumbnail_url()
            if thumbnail:
                self.art[banner_url] = Proxy.Preview(HTTP.Request(thumbnail), i)
            else:
                self.art[banner_url] = Proxy.Media(HTTP.Request(banner_url), i)

    def update_banners(self, image, i):
        banner_url = image.get_url()
        if banner_url not in self.banners:
            thumbnail = image.get_thumbnail_url()
            if thumbnail:
                self.banners[banner_url] = Proxy.Preview(HTTP.Request(thumbnail), i)
            else:
                self.banners[banner_url] = Proxy.Media(HTTP.Request(banner_url), i)

    def update_posters(self, image, i):
        banner_url = image.get_url()
        if banner_url not in self.posters:
            thumbnail = image.get_thumbnail_url()
            if thumbnail:
                self.posters[banner_url] = Proxy.Preview(HTTP.Request(thumbnail), i)
            else:
                self.posters[banner_url] = Proxy.Media(HTTP.Request(banner_url), i)

    def update_posters_for_seasons(self, image, season_numbers):
        banner_url = image.get_url()
        for season_number in season_numbers:
            if banner_url not in self.seasons[season_number].posters:
                count = len(self.seasons[season_number].posters)
                self.seasons[season_number].posters[banner_url] = Proxy.Media(HTTP.Request(banner_url), count)

    def fetch_banner_data(self):
        if self.tvdb_id is not None:
            xml = TVRageNetwork.fetchXML(TVDB_BANNER_LIST_URL % self.tvdb_id)
            if xml:
                return xml.xpath("/Banners/Banner")
        return []

    def update_seasons(self, image, season_numbers, i):
        banner_url = image.get_url()
        banner_season = image.get_season()
        if banner_season in season_numbers:
            if image.is_season_poster():
                if banner_url not in self.seasons[banner_season].posters:
                    self.seasons[banner_season].posters[banner_url] = Proxy.Media(HTTP.Request(banner_url), i)
            elif image.is_season_banner():
                if banner_url not in self.seasons[banner_season].banners:
                    self.seasons[banner_season].banners[banner_url] = Proxy.Media(HTTP.request(banner_url), i)

    def get_tvdb_id(self):
        if self.tvrage_id in TVDB_DICTIONARY:
            return TVDB_DICTIONARY[self.tvrage_id]
        else:
            return None


class TVDBImage:
    def __init__(self, xml=None):
        self.xml = xml

    def get_url(self):
        if self.xml and self.xml.xpath("./BannerPath") and self.xml.xpath("./BannerPath")[0].text is not None:
            return TVDB_BANNER_BASE_URL + self.xml.xpath("./BannerPath")[0].text
        else:
            return ''

    def get_thumbnail_url(self):
        if self.xml and self.xml.xpath("./ThumbnailPath") and self.xml.xpath("./ThumbnailPath")[0].text is not None:
            return TVDB_BANNER_BASE_URL + self.xml.xpath("./ThumbnailPath")[0].text
        else:
            return ''

    def get_score(self):
        if self.xml and self.xml.xpath("./Rating") and (self.xml.xpath("./Rating")[0].text is not None):
            return int(10 * float(self.xml.xpath("./Rating")[0].text))
        else:
            return 10

    def get_score_for_season(self):
        if self.xml and self.xml.xpath("./Rating") and (self.xml.xpath("./Rating")[0].text is not None):
            return int(float(self.xml.xpath("./Rating")[0].text))
        else:
            return 1

    def get_type(self):
        if self.xml and self.xml.xpath("./BannerType"):
            return self.xml.xpath("./BannerType")[0].text
        else:
            return None

    def get_season(self):
        if self.xml and self.xml.xpath("./Season"):
            return self.xml.xpath("./Season")[0].text
        else:
            return None

    def is_season_poster(self):
        return self.xml and self.xml.xpath("./BannerType2") and self.xml.xpath("./BannerType2")[0].text == "season"

    def is_season_banner(self):
        return self.xml and self.xml.xpath("./BannerType2") and self.xml.xpath("./BannerType2")[0].text == "seasonwide"