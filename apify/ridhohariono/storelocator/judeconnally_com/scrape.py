import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "judeconnally.com"
BASE_URL = "https://www.judeconnally.com"
LOCATION_URL = "https://judeconnally.com/pages/our-stores"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_lists = soup.find("div", {"class": "addresses"}).find_all(
        "div", {"class": "line"}
    )
    del store_lists[-1]
    locations = []
    for row in store_lists:
        page_url = LOCATION_URL
        locator_domain = DOMAIN
        location_name = row.find("h2").text.strip()
        info = row.find_all("p")
        addresess = info[0].get_text(strip=True, separator=",").split(",")
        street_address = handle_missing(addresess[0])
        city = handle_missing(addresess[1])
        state_zip_phone = addresess[2].split()
        state = handle_missing(state_zip_phone[0])
        zip_code = handle_missing(state_zip_phone[1])
        phone = " ".join(state_zip_phone[2:])
        hours_of_operation = (
            info[1]
            .get_text(strip=True, separator=",")
            .replace("Store Hours: ", "")
            .replace("–", "-")
            .replace("Hours: ", "")
            .replace(". Closed Monday & Sunday", "")
        )
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "boutiques"
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
