import csv
import re
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "medivet.co.uk"
BASE_URL = "https://www.medivet.co.uk"
LOCATION_URL = "https://www.medivet.co.uk/sitemap.xml"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36",
    "sec-fetch-site": "same-origin",
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


def parse_hours(table):
    if not table:
        return "<MISSING>"
    hoo = table.get_text(strip=True, separator=",").replace("day,", "day: ")
    return hoo


def parse_json(soup):
    info = soup.find("script", type="application/ld+json")
    if not info:
        return False
    data = json.loads(info.string)
    return data


def fetch_store_urls():
    log.info("Fetching store URL")
    soup = pull_content(LOCATION_URL)
    store_urls = []
    excluded = [
        "https://www.medivet.co.uk/vet-practices/hyde-park/hyde-park",
        "https://www.medivet.co.uk/vet-practices/hornsey/cattery/",
        "https://www.medivet.co.uk/vet-practices/south-harrow/thank-you---south-harrow/",
        "https://www.medivet.co.uk/vet-practices/hyde-park/hyde-park-pet-boutique/",
        "https://www.medivet.co.uk/vet-practices/hyde-park/hyde-park-grooming-service/",
    ]
    for val in soup.find_all("loc", text=re.compile(r"\/vet-practices\/\D+")):
        if val.text not in excluded:
            store_urls.append(val.text)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        info = parse_json(soup)
        if not info:
            continue
        locator_domain = DOMAIN
        location_name = handle_missing(info["name"].strip())
        address = info["address"][0]
        street_address = handle_missing(address["streetAddress"].strip())
        city = handle_missing(address["addressLocality"].strip())
        zip_code = (
            "<MISSING>"
            if "postalCode" not in address
            else address["postalCode"].strip()
        )
        state = (
            "<MISSING>"
            if "addressRegion" not in address
            else address["addressRegion"].strip()
        )
        country_code = address["addressCountry"]
        store_number = "<MISSING>"
        phone = handle_missing(info["telephone"])
        hours_of_operation = handle_missing(", ".join(info["openingHours"]))
        location_type = "<MISSING>"
        geo = soup.find("div", {"class": "googleMap loading"})
        latitude = handle_missing(geo["data-lat"])
        longitude = handle_missing(geo["data-lng"])
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
