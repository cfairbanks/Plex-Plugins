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
        self.reset_image_sort = Prefs["reset_image_sort"]

    def update_images(self, season_numbers, fallback_image_url=None):
        Log("update_images: START")

        data = self.fetch_banner_data()

        for xml in data:
            image = TVDBImage(xml)

            if image.is_art():
                self.update_art(image)
            elif image.is_banner():
                self.update_banners(image)
                self.update_season_banners(image, season_numbers)
            elif image.is_poster():
                self.update_posters(image)
                self.update_season_posters(image, season_numbers)
            elif image.is_season_banner():
                self.update_season_banners(image, season_numbers)
            elif image.is_season_poster():
                self.update_season_posters(image, season_numbers)

        self.update_posters_with_default_image(fallback_image_url, season_numbers)

        Log("update_images: END")

    def update_art(self, image):
        image_url = image.get_url()
        if self.reset_image_sort or image_url not in self.art:
            thumbnail_url = image.get_thumbnail_url()
            if thumbnail_url:
                self.art[image_url] = Proxy.Preview(HTTP.Request(thumbnail_url), image.get_sort_order())
            else:
                self.art[image_url] = Proxy.Media(HTTP.Request(image_url), image.get_sort_order())

    def update_banners(self, image):
        image_url = image.get_url()
        if self.reset_image_sort or image_url not in self.banners:
            thumbnail_url = image.get_thumbnail_url()
            if thumbnail_url:
                self.banners[image_url] = Proxy.Preview(HTTP.Request(thumbnail_url), image.get_sort_order())
            else:
                self.banners[image_url] = Proxy.Media(HTTP.Request(image_url), image.get_sort_order())

    def update_season_banners(self, image, season_numbers):
        image_url = image.get_url()
        for season_number in season_numbers:
            banner_season = image.get_season()
            if (banner_season is None or banner_season == season_number) and \
                    (self.reset_image_sort or image_url not in self.seasons[season_number].banners):
                thumbnail_url = image.get_thumbnail_url()
                if thumbnail_url:
                    self.seasons[season_number].banners[image_url] = Proxy.Preview(HTTP.Request(thumbnail_url),
                                                                                   image.get_sort_order_for_season())
                else:
                    self.seasons[season_number].banners[image_url] = Proxy.Media(HTTP.Request(image_url),
                                                                                 image.get_sort_order_for_season())

    def update_posters(self, image):
        image_url = image.get_url()
        thumbnail_url = image.get_thumbnail_url()
        if self.reset_image_sort or image_url not in self.posters:
            Log('adding poster ' + image_url + ' at sort %d' % image.get_sort_order())
            if thumbnail_url:
                self.posters[image_url] = Proxy.Preview(HTTP.Request(thumbnail_url), image.get_sort_order())
            else:
                self.posters[image_url] = Proxy.Media(HTTP.Request(image_url), image.get_sort_order())

    def update_season_posters(self, image, season_numbers):
        image_url = image.get_url()
        thumbnail_url = image.get_thumbnail_url()
        for season_number in season_numbers:
            banner_season = image.get_season()
            if (banner_season is None or banner_season == season_number) and \
                    (self.reset_image_sort or image_url not in self.seasons[season_number].posters):
                Log('adding season poster ' + image_url + ' at sort %d' % image.get_sort_order_for_season())
                if thumbnail_url:
                    self.seasons[season_number].posters[image_url] = Proxy.Preview(HTTP.Request(thumbnail_url),
                                                                                   image.get_sort_order_for_season())
                else:
                    self.seasons[season_number].posters[image_url] = Proxy.Media(HTTP.Request(image_url),
                                                                                 image.get_sort_order_for_season())

    def update_posters_with_default_image(self, image_url, season_numbers):
        if image_url:
            if self.reset_image_sort or image_url not in self.posters:
                Log('adding poster ' + image_url + ' at sort %d' % TVDBImage.FALLBACK_SORT_ORDER)
                self.posters[image_url] = Proxy.Media(HTTP.Request(image_url), TVDBImage.FALLBACK_SORT_ORDER)
            for season_number in season_numbers:
                if self.reset_image_sort or image_url not in self.seasons[season_number].posters:
                    Log('adding season poster ' + image_url + ' at sort %d' % TVDBImage.FALLBACK_SORT_ORDER)
                    self.seasons[season_number].posters[image_url] = Proxy.Media(HTTP.Request(image_url),
                                                                                 TVDBImage.FALLBACK_SORT_ORDER)

    def fetch_banner_data(self):
        if self.tvdb_id is not None:
            xml = TVRageNetwork.fetchXML(TVDB_BANNER_LIST_URL % self.tvdb_id)
            if xml:
                return xml.xpath("/Banners/Banner")
        return []

    def get_tvdb_id(self):
        if self.tvrage_id in TVDB_DICTIONARY:
            return TVDB_DICTIONARY[self.tvrage_id]
        else:
            return None


class TVDBImage:
    MAX_TVDB_IMAGE_RATING = 10
    FALLBACK_SORT_ORDER = 2000

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

    def get_sort_order(self):
        """
        Calculates the sort order for this image.
        Lower values of sort order are given higher priority.
        Zero is a bad sort value, use a minimum of one.
        """
        if self.get_rating() is not None:
            return int((self.MAX_TVDB_IMAGE_RATING + 1 - self.get_rating()) * 10)
        else:
            return (self.MAX_TVDB_IMAGE_RATING + 1) * 10

    def get_sort_order_for_season(self):
        """
        Calculates the sort order for this image assuming it will be used for a season image.
        If the image is of the expected season type, defer to the regular sort order.
        Lower values of sort order are given higher priority.
        """
        if self.is_season_banner() or self.is_season_poster():
            return self.get_sort_order()
        else:
            return (self.get_sort_order() + self.MAX_TVDB_IMAGE_RATING + 2) * 10

    def get_rating(self):
        if self.xml and self.xml.xpath("./Rating") and self.xml.xpath("./Rating")[0].text is not None:
            return float(self.xml.xpath("./Rating")[0].text)
        else:
            return None

    def get_type(self):
        if self.xml and self.xml.xpath("./BannerType"):
            return self.xml.xpath("./BannerType")[0].text
        else:
            return None

    def get_type2(self):
        if self.xml and self.xml.xpath("./BannerType2"):
            return self.xml.xpath("./BannerType2")[0].text
        else:
            return None

    def get_season(self):
        if self.xml and self.xml.xpath("./Season") and self.xml.xpath("./Season")[0].text is not None:
            return int(self.xml.xpath("./Season")[0].text)
        else:
            return None

    def is_art(self):
        return self.get_type() == 'fanart'

    def is_banner(self):
        return self.get_type() == 'series'

    def is_poster(self):
        return self.get_type() == 'poster'

    def is_season_poster(self):
        return self.get_type() == 'season' and self.get_type2() == "season"

    def is_season_banner(self):
        return self.get_type() == 'season' and self.get_type2() == "seasonwide"
