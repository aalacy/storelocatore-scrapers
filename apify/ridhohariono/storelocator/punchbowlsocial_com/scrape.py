import csv
import re
import usaddress
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "punchbowlsocial.com"
BASE_URL = "https://punchbowlsocial.com"
LOCATION_URL = "https://punchbowlsocial.com/find-location"
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


def fetch_store_urls():
    log.info("Fetching store URL")
    soup = pull_content(LOCATION_URL)
    store_urls = []
    for val in soup.find_all(
        "a", href=re.compile(r"https\:\/\/punchbowlsocial.com\/location\/\D+")
    ):
        city_state = val.find("p", {"class": "name"}).text.split(",")
        store_dict = {
            "link": val["href"],
            "city": city_state[0].strip(),
            "state": city_state[1].strip(),
        }
        store_urls.append(store_dict)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for row in store_urls:
        page_url = row["link"]
        soup = pull_content(page_url)
        info = (
            soup.find("div", {"id": "hours"})
            .find("div", {"class": "hours-body"})
            .find("div", {"class": "row"})
            .find_all("div")
        )
        locator_domain = DOMAIN
        location_name = soup.find("div", {"class": "title"}).text.strip()
        address = info[2].get_text(strip=True, separator=",").split(",")
        parse_addr = usaddress.tag(", ".join(address[:-1]))[0]
        city = row["city"].replace("Domain", "").strip()
        state = row["state"]
        zip_code = parse_addr["ZipCode"] if "ZipCode" in parse_addr else "<MISSING>"
        street_address = (
            address[0]
            .replace(zip_code, "")
            .replace(state, "")
            .replace(city, "")
            .replace("Austin", "")
            .strip()
        )
        country_code = "US"
        store_number = "<MISSING>"
        phone = handle_missing(address[-1])
        get_hoo = info[0].get_text(strip=True, separator=",").replace(" /,", ": ")
        hours = [val.next_sibling.strip() for val in info[0].find_all("span")]
        if "Temporarily Closed" not in get_hoo:
            if not all(x == hours[0] for x in hours):
                location_type = "OPEN"
            else:
                location_type = "TEMP_CLOSED"
        else:
            location_type = "TEMP_CLOSED"
        hours_of_operation = re.sub(
            r"21\s+.*", "", get_hoo.replace("CLOSED-", "CLOSED").strip()
        )
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
