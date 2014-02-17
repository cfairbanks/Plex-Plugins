import re


def sanitize_show_name(name):
    """
    Scrubs out casing, punctuation, and extra whitespaces which might make it harder to match a show name
    """
    # TODO - better re.sub to sanitize out all punctuation
    sanitized = name.lower().replace('!', ' ').replace(':', ' ').replace('-', ' ')
    sanitized = re.sub(r'\s+', ' ', sanitized)
    return sanitized.strip()
