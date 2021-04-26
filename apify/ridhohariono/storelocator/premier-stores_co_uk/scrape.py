import csv
import re
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "premier-stores.co.uk"
BASE_URL = "https://www.premier-stores.co.uk"
LOCATION_URL = "https://www.premier-stores.co.uk/sitemap.xml"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def write_output(data):
    log.info("Write Output of " + DOMAIN)
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 500:
        return False
    soup = bs(req.content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(table):
    if not table:
        return "<MISSING>"
    hoo = table.get_text(strip=True, separator=",").replace("day:,", "day: ")
    return hoo.replace("Day,Open,closed,", "")


def parse_json(soup):
    info = soup.find("script", type="application/ld+json").string
    data = json.loads(info)
    return data


def find_meta(soup, query):
    el = soup.find("meta", query)
    if not el:
        return "<MISSING>"
    return handle_missing(soup.find("meta", query)["content"])


def fetch_store_urls():
    log.info("Fetching store URL")
    soup = pull_content(LOCATION_URL)
    store_urls = []
    for val in soup.find_all("loc", text=re.compile(r"\/sitemap\.xml\?page\=\d+")):
        page = pull_content(val.text)
        for row in page.find_all("loc", text=re.compile(r"\/our-stores\/\D+")):
            if (
                not re.match(r".*\-0$", row.text)
                and "/woodside-convenience-store-2" not in row.text
            ):
                store_urls.append(row.text)
    store_urls = list(set(store_urls))
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        if not soup:
            continue
        locator_domain = DOMAIN
        location_name = find_meta(soup, {"name": "geo.placename"})
        street_address = find_meta(soup, {"property": "og:street_address"})
        city = find_meta(soup, {"property": "og:locality"})
        zip_code = find_meta(soup, {"property": "og:postal_code"})
        state = find_meta(soup, {"property": "og:region"})
        country_code = "GB"
        store_number = "<MISSING>"
        phone = find_meta(soup, {"property": "og:phone_number"})
        hours_of_operation = parse_hours(
            soup.find("div", {"id": "storeOpeningTimes"}).find("table")
        )
        location_type = find_meta(soup, {"property": "og:type"})
        latitude = find_meta(soup, {"property": "og:latitude"})
        longitude = find_meta(soup, {"property": "og:longitude"})
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                locator_domain,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
