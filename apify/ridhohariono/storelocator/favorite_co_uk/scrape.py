import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import re
import time

DOMAIN = "favorite.com"
BASE_URL = "https://stores.favorite.com/"
LOCATION_URL = "https://favorite.co.uk/store-finder?delivery=0&lat={}&lng={}"
AJAX_URL = "https://favorite.co.uk/ajax/storefinder"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "en-US,en;q=0.8",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
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


def pull_content(url, payload):
    log.info("Pull content => {}: {},{}".format(url, payload["lat"], payload["lng"]))
    i = 0
    while True:
        req = session.post(url, headers=HEADERS, data=payload, allow_redirects=False)
        if req.status_code == 200:
            soup = bs(req.json()["html"], "lxml")
            return soup
        else:
            i = i + 1
            if i > 2:
                return False
            time.sleep(2)
            continue


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def is_duplicate(list, filter):
    for x in list:
        if filter in x:
            return True
    return False


def parse_hours(table):
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def generate_payload():
    log.info("Fetching store URL")
    payloads = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=20,
        max_search_results=200,
    )
    for lat, long in search:
        payload = {
            "action": "init",
            "is_reload": True,
            "delivery": 0,
            "lat": lat,
            "lng": long,
        }
        payloads.append(payload)
    log.info("Found {} URL ".format(len(payloads)))
    return payloads


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = generate_payload()
    locations = []
    for payload in page_urls:
        soup = pull_content(AJAX_URL, payload)
        if not soup:
            continue
        main = soup.find("div", {"class": "row row-store mb0"})
        if not main or len(main) > 50:
            continue
        for row in main:
            content = main.find("div", {"class": "col-12 mb0"})
            location_name = (
                content.find("div", {"class": "store-name"})
                .get_text(strip=True, separator=",")
                .split(",")[0]
            )
            locator_domain = DOMAIN
            address = (
                content.find("div", {"class": "store-name"})
                .get_text(strip=True, separator=",")
                .split(",")[2:]
            )
            street_address = (
                handle_missing(address[0]).replace("\n", " ").replace("\t", "").strip()
            )
            city = handle_missing(address[1]).strip()
            state = handle_missing(address[2]).strip()
            zip_code = handle_missing(address[3]).strip()
            country_code = "UK"
            store_number = "<MISSING>"
            phone = soup.find(
                "a", {"class": "store-no", "href": re.compile(r"tel\:\/\/.*")}
            )
            if not phone:
                phone = "<MISSING>"
            else:
                phone = phone.text
            day_hours = content.find("ul", {"class": "opening-times"}).find_all(
                "li", {"class": False}
            )
            hours = []
            for x in day_hours:
                hoo = x.find("span", {"class": "ot"}).text.strip()
                hours.append(hoo)
            if all(value == "Closed" for value in hours):
                location_type = "CLOSED"
            else:
                location_type = "OPEN"
            hours_of_operation = (
                ", ".join(
                    content.find("ul", {"class": "opening-times"})
                    .get_text(strip=True, separator=",")
                    .split(",")[1:]
                )
                .replace("Delivery, ", "")
                .strip()
            )
            latitude = payload["lat"]
            longitude = payload["lng"]
            page_url = LOCATION_URL.format(latitude, longitude)
        if is_duplicate(locations, street_address):
            log.info(
                "Found duplicate => {}:{} => {}".format(
                    latitude, longitude, street_address
                )
            )
            continue
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
