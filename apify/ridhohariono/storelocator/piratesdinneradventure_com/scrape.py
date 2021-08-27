import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import json


DOMAIN = "piratesdinneradventure.com"
BASE_URL = "https://piratesdinneradventure.com/"
LOCATION_URL = "https://piratesdinneradventure.com/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_json(soup):
    info = soup.find_all("script", {"type": "application/ld+json"})[1].string
    data = json.loads(info)
    return data


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    alinks = soup.find_all("a", {"class": "menu-item-link menu-link"})
    exclude = ["About the Show", "Rent a Venue"]
    for link in alinks:
        text_link = link.get_text(strip=True, separator="|").split("|")
        if text_link[1] in exclude:
            continue
        store_urls.append(link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        if "orlando" in page_url:
            soup = pull_content(BASE_URL)
        else:
            soup = pull_content(page_url)
        data = parse_json(soup)
        locator_domain = DOMAIN
        location_name = handle_missing(data["name"])
        street_address = handle_missing(data["address"]["streetAddress"])
        city = handle_missing(data["address"]["addressLocality"])
        state = handle_missing(data["address"]["addressRegion"])
        zip_code = handle_missing(data["address"]["postalCode"])
        phone = handle_missing(data["telephone"]).replace("+", "")
        country_code = "US"
        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"
        location_type = "piratesdinneradventure"
        latitude = handle_missing(data["geo"]["latitude"])
        longitude = handle_missing(data["geo"]["longitude"])
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
