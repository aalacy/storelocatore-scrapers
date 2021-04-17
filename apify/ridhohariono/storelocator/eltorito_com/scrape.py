import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "eltorito.com"
BASE_URL = "https://www.eltorito.com"
LOCATION_URL = "https://www.eltorito.com/locations/"
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


def parse_hours(hours):
    hoo = hours.replace("day,", "day: ").strip()
    return hoo


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"class": "locations-container"})
    store_content = content.find_all("div", {"class": "location"})
    for row in store_content:
        link = row.find("h2").find("a")
        store_dict = {
            "link": link["href"],
            "store_number": row["data-location-id"],
        }
        store_urls.append(store_dict)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    sotre_info = fetch_store_urls()
    locations = []
    for row in sotre_info:
        page_url = row["link"]
        soup = pull_content(page_url)
        content = soup.find("section", {"class": "location-single"})
        locator_domain = DOMAIN
        location_name = content.select_one("div.location-header h1").text.strip()
        addr_content = content.select_one("div.location-address a.address")
        address = addr_content.text.strip().split(",")
        if len(address) < 4:
            street_address = address[0]
            city = address[1].strip()
            state = address[2].strip()
            zip_code = "<MISSING>"
        else:
            street_address = address[0]
            city = address[1]
            state = re.sub(r"\d+", "", address[2]).strip()
            zip_code = re.sub(r"\D+", "", address[2]).strip()
        country_code = "US"
        store_number = row["store_number"]
        phone = content.select_one("div.location-contact p a").text.strip()
        hours_of_operation = parse_hours(
            content.select_one("div.hours").get_text(strip=True, separator=",")
        )
        lat_long = re.sub(r".*destination=", "", addr_content["href"]).split(",")
        location_type = "<MISSING>"
        latitude = lat_long[0]
        longitude = lat_long[1]
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
