import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "nutritioncityonline.com"
BASE_URL = "https://www.nutritioncityonline.com"
LOCATION_URL = "https://nutritioncityonline.com/"
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
    return field.strip()


def get_latlong(gmap_link):
    req = session.get(gmap_link)
    lat_long = re.search(r"\/@(.*)\/", req.url).group(1).replace(",12z", "").split(",")
    return lat_long


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_lists = (
        soup.find("div", {"id": "hours-location"})
        .find("div", {"class": "d-flex align-items-stretch flex-wrap"})
        .find_all("div", {"class": re.compile(r"contact-info-.*")})
    )
    locations = []
    for row in store_lists:
        page_url = LOCATION_URL
        locator_domain = DOMAIN
        location_name = row.find("h3", {"class": "ci-title"}).text.strip()
        addresess = row.find_all("address", {"class": "ci-address"})
        phones = row.find_all("p", {"class": "ci-call-button"})
        hours_of_operation = (
            row.find("div", {"class": "ci-day-hours"})
            .get_text(strip=True, separator=",")
            .replace("–", "-")
        )
        for i in range(len(addresess)):
            addr = (
                addresess[i]
                .get_text(strip=True, separator=",")
                .replace(",,", ",")
                .split(",")
            )

            if "Coon Rapids" in addr[0]:
                street_address = handle_missing(addr[0].replace("Coon Rapids", ""))
                city = "Coon Rapids"
                state_zip = addr[1].split(" ")
                state = handle_missing(state_zip[0])
                zip_code = handle_missing(state_zip[1])
            else:
                street_address = handle_missing(addr[0])
                city = handle_missing(addr[1])
                state_zip = addr[2].strip().split(" ")
                state = handle_missing(state_zip[0])
                zip_code = handle_missing(state_zip[1])
            phone = handle_missing(phones[i].text)
            country_code = "US"
            store_number = "<MISSING>"
            if "Mega Store" in location_name:
                location_type = "Mega Store"
            else:
                location_type = "Outlet Store"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if i == 0:
                gmap_link = row.find(
                    "a", {"class": "ci-green-button view-store-button"}
                )["href"]
                lat_long = get_latlong(gmap_link)
                latitude = handle_missing(lat_long[0])
                longitude = handle_missing(lat_long[1])
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
