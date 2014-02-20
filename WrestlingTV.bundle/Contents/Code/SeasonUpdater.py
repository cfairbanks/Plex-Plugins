import Network
import tvrage


def el_text(element, xp):
    return element.xpath(xp)[0].text if element.xpath(xp) and element.xpath(xp)[0].text else ''


def parse_date(string):
    return Datetime.ParseDate(string).date()


class Updater():
    def __init__(self, metadata, media_seasons):
        self.tvrage_id = metadata.id
        self.seasons = metadata.seasons
        self.series_summary = metadata.summary
        self.media_seasons = media_seasons

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
        if season_number in self.media_seasons:
            Log("Season matched: " + season_number)
            self.seasons[season_number].summary = self.series_summary
            for episode_xml in season_xml.xpath("./episode"):
                self.update_episode(season_number, episode_xml)

    def update_episode(self, season_number, episode_xml):
        # Get the season and episode numbers
        episode_num = el_text(episode_xml, 'seasonnum')

        # Also get the air date for date-based episodes.
        try:
            originally_available_at = parse_date(el_text(episode_xml, 'airdate'))
        except:
            originally_available_at = None

        if not self.has_media(season_number, episode_num, originally_available_at):
            Log("No media for season %s episode %s - skipping population of episode data", season_number, episode_num)
            return

        # Get the episode object from the model
        episode = self.seasons[season_number].episodes[episode_num]

        # Copy attributes from the XML
        episode.title = el_text(episode_xml, 'title')
        episode.summary = el_text(episode_xml, 'summary')

        try:
            episode.absolute_number = int(el_text(episode_xml, 'epnum'))
        except:
            pass

        if originally_available_at:
            episode.originally_available_at = originally_available_at

        self.update_episode_thumbnail(episode, episode_xml)

    def has_media(self, season_number, episode_number, originally_available_at):
        if originally_available_at:
            date_based_season = originally_available_at.year
        else:
            date_based_season = None

        return (season_number in self.media_seasons and
                episode_number in self.media_seasons[season_number].episodes) or \
               (originally_available_at is not None and
                date_based_season in self.media_seasons and
                originally_available_at in self.media_seasons[date_based_season].episodes) or \
               (originally_available_at is not None and
                season_number in self.media_seasons and
                originally_available_at in self.media_seasons[season_number].episodes)

    def update_episode_thumbnail(self, episode, episode_xml):
        thumbnail_url = el_text(episode_xml, "screencap")
        if thumbnail_url and thumbnail_url not in episode.thumbs:
            episode.thumbs[thumbnail_url] = Proxy.Media(HTTP.Request(thumbnail_url))


