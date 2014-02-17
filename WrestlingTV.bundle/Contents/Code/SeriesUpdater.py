import ImageUpdater
import SeasonUpdater
import tvrage
import Network


class Updater:
    def __init__(self, metadata, media, lang, tvdb_id=None, force_refresh=False):
        self.tvrage_id = metadata.id
        self.tvdb_id = tvdb_id
        self.metadata = metadata
        self.media = media
        self.lang = lang
        self.force_refresh = force_refresh

    def update(self):
        Log("update %s: START" % self.tvrage_id)
        xml = Network.fetch_xml(tvrage.SHOW_INFO_URL % self.tvrage_id)

        self.metadata.title = xml.xpath("/Showinfo/showname")[0].text
        if xml.xpath("/Showinfo/network"):
            self.metadata.studio = xml.xpath("/Showinfo/network")[0].text
        self.metadata.duration = int(xml.xpath("/Showinfo/runtime")[0].text) * 60 * 1000
        self.metadata.originally_available_at = Datetime.ParseDate(xml.xpath("/Showinfo/started")[0].text).date()
        self.metadata.genres = [genre.text for genre in xml.xpath("/Showinfo/genres/genre")]
        if xml.xpath("/Showinfo/summary"):
            self.metadata.summary = xml.xpath("/Showinfo/summary")[0].text
        self.metadata.countries = [xml.xpath("/Showinfo/origin_country")[0].text]
        self.metadata.tags = [xml.xpath("/Showinfo/classification")[0].text]

        self.update_seasons(self.metadata, self.media)
        self.update_images(self.metadata, self.media, xml)
        Log("update: END")

    def update_seasons(self, metadata, media):
        SeasonUpdater.Updater(metadata, media.seasons).update()

    def update_images(self, metadata, media, series_xml):
        if series_xml.xpath("/Showinfo/image") and series_xml.xpath("/Showinfo/image")[0].text != None:
            fallback_image_url = series_xml.xpath("/Showinfo/image")[0].text
        else:
            fallback_image_url = None

        ImageUpdater.Updater(metadata=metadata,
                             tvdb_id=self.tvdb_id,
                             season_numbers=media.seasons,
                             fallback_image_url=fallback_image_url,
                             force_refresh=self.force_refresh).update()
