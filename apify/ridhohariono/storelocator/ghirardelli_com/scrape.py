import csv
import re
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as bs

DOMAIN = "ghirardelli.com"
BASE_URL = "https://ghirardelli.com/"
LOCATION_URL = "https://www.ghirardelli.com/wcsstore/storelocator-data/gcc_locations.json?origLat=37.721008&origLng=-122.501943&origAddress=Horse%2520Trail%252C%2520San%2520Francisco%252C%2520CA%252094132%252C%2520Amerika%2520Serikat&formattedAddress=&boundsNorthEast=&boundsSouthWest=&storeId=11003&langId=-1&origLat=37.721008&origLng=-122.501943&origAddress=Horse%2520Trail%252C%2520San%2520Francisco%252C%2520CA%252094132%252C%2520Amerika%2520Serikat&formattedAddress=&boundsNorthEast=&boundsSouthWest="
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(url):
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    hours_content = soup.find("div", {"class": "panel"})
    if not hours_content.find("table"):
        check = hours_content.text
        if "Temporarily closed" in check:
            return "<MISSING>"
    else:
        hours_content = hours_content.find("table")
    hours = hours_content.get_text(strip=True, separator=",").replace("day,", "day: ")
    if "Temporarily Closed" in hours:
        return "<MISSING>"
    hoo = re.sub(r"Ice cream fountain opens daily at \d{1,2}:\d{2} \D{2},", "", hours)
    return hoo


def fetch_data():
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in store_info:
        page_url = row["web"]
        location_name = handle_missing(row["name"])
        if "address2" in row and len(row["address2"]) > 0:
            street_address = "{}, {}".format(row["address"], row["address2"])
        else:
            street_address = row["address"]
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["postal"])
        country_code = "US"
        store_number = row["id"]
        phone = handle_missing(row["phone"])
        latitude = handle_missing(row["lat"])
        longitude = handle_missing(row["lng"])
        hours_of_operation = parse_hours(page_url)
        if hours_of_operation == "<MISSING>":
            location_type = "TEMP_CLOSED"
        else:
            location_type = "OPEN"
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                DOMAIN,
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
