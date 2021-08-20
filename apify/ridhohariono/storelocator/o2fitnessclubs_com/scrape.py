import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "o2fitnessclubs.com"
BASE_URL = "https://www.o2fitnessclubs.com"
LOCATION_URL = "https://www.o2fitnessclubs.com/locations"
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


def parse_hours(element):
    if not element:
        return "<MISSING>"
    days = [val.text for val in element.find_all("p", text=re.compile(r"day.*"))]
    hours = [
        val.text for val in element.find_all("h5", text=re.compile(r"\d{1,2}\s+am|pm"))
    ]
    hoo = []
    for i in range(len(days)):
        hoo.append(
            "{}: {}".format(days[i].replace("–", "-"), hours[i].replace("–", "-"))
        )
    return ", ".join(hoo)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find_all("div", {"class": "hs-accordion__item-content"})
    for row in content:
        stores = row.find("ul").find_all("a")
        for link in stores:
            store_urls.append(BASE_URL + link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        comming_soon = soup.find("div", {"class": "location-description"}).find("h6")
        if comming_soon and "COMING SOON" in comming_soon:
            continue
        locator_domain = DOMAIN
        location_name = soup.find("title").text.strip()
        address = soup.find("div", {"class": "location-details"})
        street_address = address.find("div", {"class": "street-address"}).text.strip()
        city_state_zip = (
            address.find("div", {"class": "city-state-zip"}).text.strip().split(",")
        )
        city = city_state_zip[0]
        state = re.sub(r"\d+", "", city_state_zip[1])
        zip_code = re.sub(r"\D+", "", city_state_zip[1])
        phone = address.find("div", {"class": "location-phone"}).text.strip()
        country_code = "US"
        store_number = re.search(
            r"\?store_id=(\d+)",
            soup.find("a", {"href": re.compile(r"\?store_id=\d+")})["href"],
        ).group(1)
        hours_of_operation = parse_hours(soup.find("div", {"class": "location-hours"}))
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
