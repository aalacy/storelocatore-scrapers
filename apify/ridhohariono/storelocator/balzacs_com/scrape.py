import re
import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "balzacs.com"
BASE_URL = "https://shop.balzacs.com"
LOCATION_URL = "https://shop.balzacs.com/pages/locations"
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


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    stores = soup.find_all("div", {"class": "location-row"})
    for store in stores:
        link = store.find("h2").find("a")["href"]
        if "shop.balzacs.com" not in link:
            link = BASE_URL + link
        store_urls.append(link)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        row = soup.find("div", {"class": "location-details"})
        locator_domain = DOMAIN
        location_name = handle_missing(row.find("h2").text.strip())
        address = (
            row.find("div", {"class": "location-address"})
            .get_text(strip=True, separator=",")
            .split(",")
        )
        zip_code = "<MISSING>"
        if len(address) > 4:
            if "L0J 1C0" in address:
                street_address = handle_missing(address[0])
                city = handle_missing(address[1])
                state = handle_missing(address[2])
                zip_code = handle_missing(address[3])
            elif "St. Catharines" in address:
                street_address = handle_missing(address[0])
                city = handle_missing(address[1])
                state = handle_missing(address[3])
            else:
                street_address = ", ".join(address[:2])
                city = handle_missing(address[2])
                state = handle_missing(address[3])
        else:
            street_address = handle_missing(address[0])
            city = handle_missing(address[1])
            state = handle_missing(address[2])
        country_code = "CA"
        store_number = "<MISSING>"
        phone = row.find("div", {"class": "location-phone"}).text.strip()
        location_type = "<MISSING>"
        hours_of_operation = row.find(
            "strong", {"class": "location-working-days"}
        ).text.strip(" ")
        hours_of_operation = re.sub(r"\*.*", "", hours_of_operation).replace(
            "pm", "pm "
        )
        if "RE-OPENING" in hours_of_operation:
            hours_of_operation = "TEMPORARILY CLOSED"
            location_type = "TEMP_CLOSED"
        geo = row.find("div", {"class": "location-address"}).find("a")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            gmap_link = geo["href"]
            lat_long = re.findall(r"\/\@(.*)z/", gmap_link)
            if lat_long:
                lat_long = lat_long[0].split(",")
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
