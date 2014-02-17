import Network
import tvrage

MAX_ALTERNATE_TITLE_SEARCHES = 2


class Searcher:
    def __init__(self, results, show_names, year, lang, force_refresh=False, start_score=60):
        self.results = results
        self.show_names = show_names
        self.lang = lang
        self.force_refresh = force_refresh
        self.start_score = start_score

    def search(self):
        """
        Searches by the show_names values and builds up the results list
        """
        Log("search %s: START" % self.show_names)

        self.search_by_tvrage_id()
        self.search_by_tvrage_string()
        self.check_alternate_titles()

        Log("search: END")

    def search_by_tvrage_id(self):
        """
        If the show input is an integer, search by TVRage ID first, scoring the result using start_score.
        """
        if len(self.show_names) == 1 and self.show_names[0].isdigit():
            xml = Network.fetch_xml(tvrage.SHOW_INFO_URL % self.show_names[0])
            if xml:
                result = MetadataSearchResult(id=str(xml.xpath("/Showinfo/showid")[0].text),
                                              name=str(xml.xpath("/Showinfo/showname")[0].text),
                                              year=xml.xpath("/Showinfo/started")[0].text,
                                              score=self.start_score,
                                              lang=self.lang)
                self.results.Append(result)
                Log(repr(result))

    def search_by_tvrage_string(self):
        """
        Search using TVRage's search API, with a string show name input.
        If it matches exactly (ignoring hyphens), then consider it a 100% match.
        Otherwise, score each potential match starting from the start_score.
        """
        for show_name in self.show_names:
            url = tvrage.SEARCH_URL % String.Quote(show_name, True)
            xml = Network.fetch_xml(url)

            i = 0
            for show_xml in xml.xpath("//show"):
                i += 1
                result_show = str(show_xml.xpath("./name")[0].text)

                if tvrage.sanitize_show_name(show_name) == tvrage.sanitize_show_name(result_show):
                    Log("Found exact match in title %s" % result_show)
                    score = 100
                else:
                    score = self.start_score - i

                nextResult = MetadataSearchResult(id=str(show_xml.xpath("./showid")[0].text),
                                                  name=result_show,
                                                  year=show_xml.xpath("./started")[0].text,
                                                  score=score,
                                                  lang=self.lang)
                self.results.Append(nextResult)
                Log(repr(nextResult))

    def check_alternate_titles(self):
        """
        Checks up to the top MAX_ALTERNATE_TITLE_SEARCHES regular matches to see if we match an alternate title.
        """
        self.results.Sort('score', descending=True)
        top_match_counter = 0
        for result in self.results:
            top_match_counter += 1
            if result.score == 100:
                return
            elif top_match_counter <= MAX_ALTERNATE_TITLE_SEARCHES:
                xml = Network.fetch_xml(tvrage.SHOW_INFO_URL % result.id)

                if xml:
                    for aka_xml in xml.xpath("./akas/aka"):
                        for show_name in self.show_names:
                            aka_show_name = str(aka_xml.text)
                            Log("[%s] [%s]" %
                                (tvrage.sanitize_show_name(show_name), tvrage.sanitize_show_name(aka_show_name)))
                            if tvrage.sanitize_show_name(show_name) == tvrage.sanitize_show_name(aka_show_name):
                                Log("Found exact match in alternate title %s" % aka_show_name)
                                result.score = 100
