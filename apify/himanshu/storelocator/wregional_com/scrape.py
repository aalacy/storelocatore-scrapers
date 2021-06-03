import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "wregional.com"
BASE_URL = "https://wregional.com"
LOCATION_URL = "https://www.wregional.com/main/dialysis-centers-locations"
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


def is_multiple(location_name, locations):
    for row in locations:
        if location_name in row:
            return False
    return True


def get_hoo(link):
    soup = pull_content(link)
    hoo = soup.find("div", {"class": "branch-hours"}).find_all("p")
    hoo = hoo[1].find("span")
    hours_of_operations = "{}: {}".format(hoo.text, hoo.next_sibling.strip())
    return hours_of_operations


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"class": "page-content"}).find_all("strong")
    locations = []
    for row in content:
        location_name = row.text
        street_address = row.next_sibling.next_sibling.strip()
        info = row.next_sibling.next_sibling.next_sibling.next_sibling.strip().split(
            ","
        )
        city = info[0]
        state = info[1].split(" ")[1]
        zip_code = info[1].split(" ")[2]
        country_code = "US"
        store_number = "<MISSING>"
        phone = row.find_next("a").text
        hours_of_operation = (
            row.find_next("a")
            .next_sibling.find_next(text=True)
            .find_next(text=True)
            .strip()
            .replace(" or later as needed for patient care", "")
            .replace("–", "-")
        )
        if "Dialysis Center" in location_name:
            location_type = "DIALYSIS_CENTER"
        elif "Home Dialysis" in location_name:
            location_type = "HOME_DIALYSIS"
        else:
            location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                DOMAIN,
                LOCATION_URL,
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
