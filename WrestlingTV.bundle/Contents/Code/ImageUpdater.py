import Network

TVDB_API_KEY = '607FE3FE16EDB11F'
TVDB_BANNER_LIST_URL = 'http://thetvdb.com/api/%s/series/%%s/banners.xml' % TVDB_API_KEY
TVDB_BANNER_BASE_URL = 'http://thetvdb.com/banners/'


class Updater():
    def __init__(self, metadata, tvdb_id=None, season_numbers=None, fallback_image_url=None, force_refresh=False):
        self.tvrage_id = metadata.id
        self.art = metadata.art
        self.banners = metadata.banners
        self.posters = metadata.posters
        self.seasons = metadata.seasons
        self.tvdb_id = tvdb_id
        self.season_numbers = season_numbers
        self.fallback_image_url = fallback_image_url
        self.reset_image_sort = force_refresh

    def update(self):
        Log("update %s: START" % self.tvrage_id)

        data = self.fetch_banner_data()

        for xml in data:
            image = TVDBImage(xml)

            if image.is_art():
                self.update_art(image)
            elif image.is_banner():
                self.update_banners(image)
                self.update_season_banners(image)
            elif image.is_poster():
                self.update_posters(image)
                self.update_season_posters(image)
            elif image.is_season_banner():
                self.update_season_banners(image)
            elif image.is_season_poster():
                self.update_season_posters(image)

        self.update_posters_with_default_image()

        Log("update: END")

    def update_art(self, image):
        image_url = image.get_url()
        if self.reset_image_sort or image_url not in self.art:
            Log('adding art %s at sort %d' % (image_url, image.get_sort_order()))
            thumbnail_url = image.get_thumbnail_url()
            if thumbnail_url:
                self.art[image_url] = Proxy.Preview(HTTP.Request(thumbnail_url), image.get_sort_order())
            else:
                self.art[image_url] = Proxy.Media(HTTP.Request(image_url), image.get_sort_order())

    def update_banners(self, image):
        image_url = image.get_url()
        if self.reset_image_sort or image_url not in self.banners:
            Log('adding banner %s at sort %d' % (image_url, image.get_sort_order()))
            thumbnail_url = image.get_thumbnail_url()
            if thumbnail_url:
                self.banners[image_url] = Proxy.Preview(HTTP.Request(thumbnail_url), image.get_sort_order())
            else:
                self.banners[image_url] = Proxy.Media(HTTP.Request(image_url), image.get_sort_order())

    def update_season_banners(self, image):
        image_url = image.get_url()
        image_season = image.get_season()

        for season_number in self.season_numbers:
            if (image_season is None or image_season == int(season_number)) and \
                    (self.reset_image_sort or image_url not in self.seasons[season_number].banners):
                Log('adding season %s banner %s at sort %d' % (season_number, image_url, image.get_sort_order()))
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

    def update_season_posters(self, image):
        image_url = image.get_url()
        thumbnail_url = image.get_thumbnail_url()
        image_season = image.get_season()

        for season_number in self.season_numbers:
            if (image_season is None or image_season == int(season_number)) and \
                    (self.reset_image_sort or image_url not in self.seasons[season_number].posters):
                Log('adding season %s poster %s at sort %d' % (
                    season_number, image_url, image.get_sort_order_for_season()))
                if thumbnail_url:
                    self.seasons[season_number].posters[image_url] = Proxy.Preview(HTTP.Request(thumbnail_url),
                                                                                   image.get_sort_order_for_season())
                else:
                    self.seasons[season_number].posters[image_url] = Proxy.Media(HTTP.Request(image_url),
                                                                                 image.get_sort_order_for_season())

    def update_posters_with_default_image(self):
        image_url = self.fallback_image_url
        if image_url:
            if self.reset_image_sort or image_url not in self.posters:
                Log('adding poster %s at sort %d' % (image_url, TVDBImage.FALLBACK_SORT_ORDER))
                self.posters[image_url] = Proxy.Media(HTTP.Request(image_url), TVDBImage.FALLBACK_SORT_ORDER)
            for season_number in self.season_numbers:
                if self.reset_image_sort or image_url not in self.seasons[season_number].posters:
                    Log('adding season %s poster %s at sort %d' % (
                        season_number, image_url, TVDBImage.FALLBACK_SORT_ORDER))
                    self.seasons[season_number].posters[image_url] = Proxy.Media(HTTP.Request(image_url),
                                                                                 TVDBImage.FALLBACK_SORT_ORDER)

    def fetch_banner_data(self):
        if self.tvdb_id is not None:
            xml = Network.fetch_xml(TVDB_BANNER_LIST_URL % self.tvdb_id)
            if xml:
                return xml.xpath("/Banners/Banner")
        return []


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
