import re
import time
import TVRageSearcher

GOOGLE_JSON_TVRAGE = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=large&q=site:tvrage.com+intitle:%s+intitle:%s+%s'


class Searcher():
    def __init__(self, results, media, lang, force_refresh=False, start_score=20):
        self.results = results
        self.show_input = media.show

        if media.year:
            self.year_input = media.year
        else:
            self.year_input = ''

        self.media = media
        self.lang = lang
        self.force_refresh = force_refresh
        self.start_score = start_score

    def search(self):
        Log("search %s (%s): START" % (self.show_input, self.year_input))
        result_urls = self.fetch_result_urls()
        i = 0
        for result_url in result_urls:
            tvrage_id = get_tvrage_id_from_url(result_url)
            if tvrage_id is not None:
                Log("found tvrage ID %s" % tvrage_id)
                score = self.start_score - i
                TVRageSearcher.Searcher(results=self.results,
                                        show_names=[tvrage_id],
                                        year=self.year_input,
                                        lang=self.lang,
                                        force_refresh=self.force_refresh,
                                        start_score=score).search_by_tvrage_id()
                i += 1
        Log("search: END")

    def fetch(self, url):
        res = JSON.ObjectFromURL(url)
        if res['responseStatus'] != 200:
            time.sleep(0.5)
            res = JSON.ObjectFromURL(url, cacheTime=0)
        time.sleep(0.5)
        return res

    def fetch_result_urls(self):
        clean_tv_show = String.Quote('"tv show"'.encode('utf-8'), usePlus=True)
        clean_show_name = String.Quote(('"' + self.show_input + '"').encode('utf-8'), usePlus=True)
        url = GOOGLE_JSON_TVRAGE % (clean_tv_show, clean_show_name, self.year_input)

        results_json = self.fetch(url)['responseData']['results']

        result_urls = []

        if len(results_json) > 0:
            for result in results_json:
                result_url = result['unescapedUrl']

                if url:
                    Log("found url " + result_url)
                    result_urls.append(result_url)

        return result_urls


def get_tvrage_id_from_url(url):
    pattern = "(?<=tvrage.com/shows/id-)\d+"
    match = re.search(pattern, url)
    if match:
        return match.group(0)
    else:
        return None
