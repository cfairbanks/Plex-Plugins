import re

# TODO - wait for tvrage to approve this API key
# API_KEY = 'bX9ymM850oC0KCZ88YZn'

API_KEY = 'P8q4BaUCuRJPYWys3RBV'
SEARCH_URL = 'http://services.tvrage.com/myfeeds/search.php?key=%s&show=%%s' % API_KEY
SHOW_INFO_URL = 'http://services.tvrage.com/myfeeds/showinfo.php?key=%s&sid=%%s' % API_KEY
EPISODE_LIST_URL = 'http://services.tvrage.com/myfeeds/episode_list.php?key=%s&sid=%%s' % API_KEY


def sanitize_show_name(name):
    """
    Scrubs out casing, punctuation, and extra whitespaces which might make it harder to match a show name
    """
    # TODO - better re.sub to sanitize out all punctuation
    sanitized = name.lower().replace('!', ' ').replace(':', ' ').replace('-', ' ')
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized.strip()
