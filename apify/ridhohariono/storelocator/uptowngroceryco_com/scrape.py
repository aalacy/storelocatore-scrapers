import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "uptowngroceryco.com"
BASE_URL = "https://www.uptowngroceryco.com"
LOCATION_URL = "https://uptowngroceryco.com/locations"
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
    if not gmap_link:
        return "<MISSING>", "<MISSING>"
    lat_long = (
        gmap_link["href"]
        .replace("http://www.google.com/maps/place/", "")
        .strip()
        .split(",")
    )
    return lat_long[0], lat_long[1]


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_lists = (
        soup.find_all("div", {"class": "container"})[3]
        .find("div", {"class": "col-md-8"})
        .find_all("div", {"class": "panel-body"})
    )
    locations = []
    for row in store_lists:
        page_url = LOCATION_URL
        locator_domain = DOMAIN
        location_name = row.find("h2").text.strip()
        details = row.find("div", {"class": "col-md-5"}).find_all("p")
        address = details[2].get_text(strip=True, separator=",").split(",")
        street_address = handle_missing(address[0])
        city = handle_missing(address[1])
        state_zip = address[2].split()
        state = handle_missing(state_zip[0])
        zip_code = handle_missing(state_zip[1])
        phone = handle_missing(details[3].text).replace("Phone", "")
        hours_of_operation = handle_missing(
            details[4]
            .text.replace(", until further notice", "")
            .replace("Store Hours", "")
        )
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "PHARMACY"
        latitude, longitude = get_latlong(row.find("a"))
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
