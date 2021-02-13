import csv
from urllib.request import urlopen
from sgrequests import SgRequests
import gzip
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests_random_user_agent  # ignore_check # noqa F401
from sglogging import sglog


thread_local = threading.local()
log = sglog.SgLogSetup().get_logger(logger_name="westernunion.com")
crawled_urls = []


def sleep(min=0.5, max=2.5):
    duration = random.uniform(min, max)
    time.sleep(duration)


def get_time():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)


def get_session(reset=False):
    # give each thread its own session object.
    # when using proxy, each thread's session will have a unique IP, and we'll switch IPs every 10 requests
    if (
        (not hasattr(thread_local, "session"))
        or (hasattr(thread_local, "request_count") and thread_local.request_count == 10)
        or (reset is True)
    ):
        thread_local.session = SgRequests(retry_behavior=False)

        reset_request_count()

    return thread_local.session


def reset_request_count():
    if hasattr(thread_local, "request_count"):
        thread_local.request_count = 0


def increment_request_count():
    if not hasattr(thread_local, "request_count"):
        thread_local.request_count = 1
    else:
        thread_local.request_count += 1


def get(url, attempt=1):

    if attempt == 11:
        log.debug(f"could not get {url} after {attempt-1} tries")
        return None

    r = None
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,la;q=0.8",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
        # the `requests_random_user_agent` package automatically rotates user-agent strings
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }

    try:
        sleep()
        session = get_session()

        session.clear_cookies()
        r = session.get(url, headers=headers)
        r.raise_for_status()

        increment_request_count()

    except (Exception) as err:
        # attempt to handle errors such as "cannot connect to proxy, timed out"
        log.debug(
            f"***** error getting {url} on thread {threading.current_thread().ident}"
        )
        log.debug(err)
        log.debug("****** resetting session")
        session = get_session(reset=True)
        # try this request again
        return get(url, attempt=attempt + 1)

    return r


def write_output(data):
    """
    The data.csv could have existing records that were preserved from the crawl prior to
    an Apify host migration. This version of write_output will append new records rather than overwriting.
    """
    with open("data.csv", mode="a+") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        output_file.seek(0)
        has_header = "street_address" in output_file.readline()
        if not has_header:
            writer.writerow(
                [
                    "locator_domain",
                    "page_url",
                    "location_name",
                    "street_address",
                    "city",
                    "state",
                    "zip",
                    "country_code",
                    "store_number",
                    "phone",
                    "location_type",
                    "latitude",
                    "longitude",
                    "hours_of_operation",
                ]
            )
        for row in data:
            writer.writerow(row)


def read_data_csv():
    try:
        with open("data.csv", mode="r") as input_file:
            csv_reader = csv.reader(input_file)
            next(csv_reader)  # skip header
            data = list(csv_reader)
        return data
    except Exception:
        log.info("Could not open data.csv")
        return []


def get_location(loc):
    website = "westernunion.com"
    typ = "Location"
    store = "<MISSING>"
    hours = "<MISSING>"
    city = ""
    add = ""
    state = ""
    zc = ""
    if "/us/" in loc:
        country = "US"
    if "/ca/" in loc:
        country = "CA"
    name = ""
    phone = ""
    lat = ""
    lng = ""
    store = loc.rsplit("/", 1)[1]
    log.debug(f"Pulling Location {loc}")
    r = get(loc)
    if not r:
        return None
    lines = r.iter_lines(decode_unicode=True)
    AFound = False
    for line in lines:
        if '"name":"' in line:
            name = line.split('"name":"')[1].split('"')[0]
        if '"streetAddress":"' in line and AFound is False:
            AFound = True
            add = line.split('"streetAddress":"')[1].split('"')[0]
        if '"city":"' in line:
            city = line.split('"city":"')[1].split('"')[0]
        if '"state":"' in line:
            state = line.split('"state":"')[1].split('"')[0]
        if '"postal":"' in line:
            zc = line.split('"postal":"')[1].split('"')[0]
        if '"geoQualitySort":' in line:
            phone = (
                line.split('"geoQualitySort":')[1].split('"phone":"')[1].split('"')[0]
            )
        if '"latitude":' in line:
            lat = line.split('"latitude":')[1].split(",")[0]
        if '"longitude":' in line:
            lng = line.split('"longitude":')[1].split(",")[0]
        if '"monCloseTime":"' in line:
            hours = (
                "Mon: "
                + line.split('"monOpenTime":"')[1].split('"')[0]
                + "-"
                + line.split('"monCloseTime":"')[1].split('"')[0]
            )
            hours = (
                hours
                + "; Tue: "
                + line.split('"tueOpenTime":"')[1].split('"')[0]
                + "-"
                + line.split('"tueCloseTime":"')[1].split('"')[0]
            )
            hours = (
                hours
                + "; Wed: "
                + line.split('"wedOpenTime":"')[1].split('"')[0]
                + "-"
                + line.split('"wedCloseTime":"')[1].split('"')[0]
            )
            hours = (
                hours
                + "; Thu: "
                + line.split('"thuOpenTime":"')[1].split('"')[0]
                + "-"
                + line.split('"thuCloseTime":"')[1].split('"')[0]
            )
            hours = (
                hours
                + "; Fri: "
                + line.split('"friOpenTime":"')[1].split('"')[0]
                + "-"
                + line.split('"friCloseTime":"')[1].split('"')[0]
            )
            hours = (
                hours
                + "; Sat: "
                + line.split('"satOpenTime":"')[1].split('"')[0]
                + "-"
                + line.split('"satCloseTime":"')[1].split('"')[0]
            )
            hours = (
                hours
                + "; Sun: "
                + line.split('"sunOpenTime":"')[1].split('"')[0]
                + "-"
                + line.split('"sunCloseTime":"')[1].split('"')[0]
            )
    return [
        website,
        loc,
        name,
        add,
        city,
        state,
        zc,
        country,
        store,
        phone,
        typ,
        lat,
        lng,
        hours,
    ]


def get_location_urls_from_sitemaps():
    """
    Download sitemaps to get the list of URLs for U.S. locations.
    """
    locs = []
    for x in range(1, 15):
        log.info("Pulling Sitemap %s..." % str(x))
        smurl = "http://locations.westernunion.com/sitemap-" + str(x) + ".xml.gz"
        with open("branches.xml.gz", "wb") as f:
            f.write(urlopen(smurl).read())
            f.close()
            with gzip.open("branches.xml.gz", "rt") as f:
                for line in f:
                    if "<loc>http://locations.westernunion.com/us/" in line:
                        url = line.split("<loc>")[1].split("<")[0]
                        url = url.replace("http://", "https://")
                        if url not in locs:
                            locs.append(url)
        log.info(str(len(locs)) + " Total Locations Found...")
    locs.sort()
    return locs


def get_crawled_urls():
    """
    If there is any data from this crawl that was persisted after an Apify host migration,
    load these records and return the URLs that were already crawled.
    """
    previous_data = read_data_csv()
    log.info(f"Recovered {len(previous_data)} records crawled prior to last migration.")
    return [d[1] for d in previous_data]


def remove_previously_crawled(sitemap_urls, already_crawled_urls):
    """
    If there is any data from this crawl that was persisted after an Apify host migration,
    load these records and remove them from the complete list of URLs to crawl.
    """
    already_crawled_urls.sort()
    urls_to_crawl = [url for url in sitemap_urls if url not in already_crawled_urls]
    return urls_to_crawl


def fetch_data(locs):
    global crawled_urls
    with ThreadPoolExecutor(max_workers=128) as executor:
        futures = [executor.submit(get_location, url) for url in locs]
        for result in as_completed(futures):
            location = result.result()
            if location and location[1] not in crawled_urls:
                crawled_urls.append(location[1])
                yield location


def scrape():
    global crawled_urls

    sitemap_urls = get_location_urls_from_sitemaps()
    log.info(f"Found {len(sitemap_urls)} locations from site maps ...")

    crawled_urls = get_crawled_urls()
    log.info(f"Already crawled {len(crawled_urls)} URLs in previous run.")

    urls_to_crawl = remove_previously_crawled(sitemap_urls, crawled_urls)
    log.info(f"{len(urls_to_crawl)} locations left to crawl ...")

    data = fetch_data(urls_to_crawl)
    write_output(data)


scrape()
