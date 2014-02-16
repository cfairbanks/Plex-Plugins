import TVRageNetwork


class Searcher:
    def __init__(self, results, media, lang, manual):
        self.results = results
        self.show_input = media.show
        self.media = media
        self.lang = lang

    # TODO - when you unmatch a show and try to correct the match, plex doesn't automatically search
    def search(self):
        Log("search %s: START" % self.show_input)

        self.search_by_tvrage_id()

        search_url = TVRageNetwork.TVRAGE_SEARCH_URL % String.Quote(self.show_input, True)
        search_xml = TVRageNetwork.fetchXML(search_url)
        curscore = 49

        show_name_from_server = search_xml.xpath("//show/name")[0].text if search_xml.xpath("//show/name") else ''

        if self.show_input.lower().replace('-', ' ') == show_name_from_server.lower().replace('-', ' '):
            curscore = 100
        for match in search_xml.xpath("//show"):
            nextResult = MetadataSearchResult(id=str(match.xpath("./showid")[0].text),
                                              name=str(match.xpath("./name")[0].text),
                                              year=match.xpath("./started")[0].text,
                                              score=curscore,
                                              lang=self.lang)
            self.results.Append(nextResult)
            Log(repr(nextResult))
            curscore = curscore - 1

        Log("search: END")

    def search_by_tvrage_id(self):
        if self.show_input.isdigit():
            xml = TVRageNetwork.fetchXML(TVRageNetwork.TVRAGE_SHOW_INFO_URL % String.Quote(self.show_input, True))
            if xml:
                result = MetadataSearchResult(id=str(xml.xpath("/Showinfo/showid")[0].text),
                                              name=str(xml.xpath("/Showinfo/showname")[0].text),
                                              year=xml.xpath("/Showinfo/started")[0].text,
                                              score=100,
                                              lang=self.lang)
                self.results.Append(result)
                Log(repr(result))

    def search_by_tvrage_string(self):
        xml = TVRageNetwork.fetchXML(TVRageNetwork.TVRAGE_SEARCH_URL % String.Quote(self.show_input, True))

        i = 0
        for show_xml in xml.xpath("//show"):
            i += 1
            show_name = str(show_xml.xpath("./name")[0].text)

            if self.show_input.lower().replace('-', ' ') == show_name.lower().replace('-', ' '):
                score = 100
            else:
                score = 50 - i

            result = MetadataSearchResult(id=str(show_xml.xpath("./showid")[0].text),
                                          name=str(show_xml.xpath("./name")[0].text),
                                          year=show_xml.xpath("./started")[0].text,
                                          score=score,
                                          lang=self.lang)
            self.results.Append(result)
            Log(repr(result))
