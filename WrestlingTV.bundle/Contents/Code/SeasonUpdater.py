import Network
import tvrage


class Updater():
    def __init__(self, metadata, season_numbers):
        self.tvrage_id = metadata.id
        self.seasons = metadata.seasons
        self.series_summary = metadata.summary
        self.season_numbers = season_numbers

    def update(self):
        """
        Fetches the detailed episode info for all seasons and updates each season's metadata.
        """
        Log("update %s: START" % self.tvrage_id)

        xml = Network.fetch_xml(tvrage.EPISODE_LIST_URL % self.tvrage_id)
        if xml:
            for season_xml in xml.xpath("/Show/Episodelist/Season"):
                self.update_season(season_xml)
        else:
            Log("no xml response from tvrage")

        Log("update: END")

    def update_season(self, season_xml):
        """
        Updates the season summary from the series summary (tvrage does not provide separate season summaries)
        Updates the episodes from the season XML
        """
        season_number = season_xml.get("no")
        if season_number in self.season_numbers:
            Log("Season matched: " + season_number)
            self.seasons[season_number].summary = self.series_summary
            for episode_xml in season_xml.xpath("./episode"):
                self.update_episode(season_number, episode_xml)

    def update_episode(self, season_number, episode_xml):
        episode_number = str(int(episode_xml.xpath("./seasonnum")[0].text))
        if episode_number in self.season_numbers[season_number].episodes:
            Log("Episode matched: " + episode_number)
            ep_object = self.seasons[season_number].episodes[episode_number]
            ep_object.title = episode_xml.xpath("./title")[0].text
            if episode_xml.xpath("./summary"):
                ep_object.summary = episode_xml.xpath("./summary")[0].text
            try:
                Log("Date: " + str(Datetime.ParseDate(episode_xml.xpath("./airdate")[0].text).date()))
                ep_object.originally_available_at = Datetime.ParseDate(episode_xml.xpath("./airdate")[0].text).date()
            except ValueError as e:
                Log(e)
            Log("Abs: " + str(int(episode_xml.xpath("./epnum")[0].text)))
            ep_object.absolute_index = int(episode_xml.xpath("./epnum")[0].text)
            if len(episode_xml.xpath("./screencap")) > 0:
                thumbnail_url = episode_xml.xpath("./screencap")[0].text
                if thumbnail_url not in ep_object.thumbs:
                    ep_object.thumbs[thumbnail_url] = Proxy.Media(HTTP.Request(thumbnail_url))
