import time

netLock = Thread.Lock()

# Keep track of success/failures in a row.
successCount = 0
failureCount = 0

MIN_RETRY_TIMEOUT = 2
RETRY_TIMEOUT = MIN_RETRY_TIMEOUT
TOTAL_TRIES = 3

headers = {'User-agent': 'Plex/Nine'}


def fetch_xml(url):
    data = fetch(url)

    if (data):
        return XML.ElementFromString(data)
    else:
        return None


def fetch(url, fetch_content=True):
    global successCount
    global failureCount
    global RETRY_TIMEOUT

    try:
        netLock.acquire()
        Log("Retrieving URL: " + url)

        tries = TOTAL_TRIES
        while tries > 0:

            result = None

            try:
                result = HTTP.Request(url, headers=headers, timeout=60)

                if fetch_content:
                    result = result.content

            except Ex.HTTPError, e:
                # Fast fail a not found.
                if e.code == 404:
                    return None

            except Ex.URLError, e:
                Log(e.reason)
                return None

            except:
                Log("fetch exception, retrying: " + e.reason)

            if result is not None:
                failureCount = 0
                successCount += 1

                if successCount > 20:
                    RETRY_TIMEOUT = max(MIN_RETRY_TIMEOUT, RETRY_TIMEOUT / 2)
                    successCount = 0

                # DONE!
                return result

            else:
                failureCount += 1
                Log("Failure (%d in a row)" % failureCount)
                successCount = 0
                time.sleep(RETRY_TIMEOUT)

                if failureCount > 5:
                    RETRY_TIMEOUT = min(10, RETRY_TIMEOUT * 1.5)
                    failureCount = 0

            tries -= 1

    finally:
        netLock.release()

    return None
