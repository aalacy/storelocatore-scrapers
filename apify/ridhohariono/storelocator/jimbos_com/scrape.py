import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import usaddress


DOMAIN = "jimbos.com"
BASE_URL = "https://jimbos.com/"
LOCATION_URL = "https://jimbos.com/locations/"
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
    store_urls = []
    soup = pull_content(LOCATION_URL)
    a_class = "elementor-post__thumbnail__link"
    alinks = soup.find_all("a", {"class": a_class})
    for link in alinks:
        store_urls.append(link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        locator_domain = DOMAIN
        location_name = soup.find("h2", {"class": "ae-element-post-title"}).text.strip()
        content = soup.find("section", {"class": "elementor-element-1b0bd78d"}).find(
            "div", {"class": "elementor-column-wrap elementor-element-populated"}
        )
        detail_list = content.find_all(
            "h5", {"class": "elementor-heading-title elementor-size-default"}
        )
        address = (
            detail_list[1]
            .get_text(strip=True, separator=",")
            .replace("Address: Jimbo's ", "")
            .split(",")
        )
        del address[0]
        parse_addr = usaddress.tag(", ".join(address).strip())
        city = parse_addr[0]["PlaceName"].strip()
        state = parse_addr[0]["StateName"].strip()
        zip_code = parse_addr[0]["ZipCode"].strip()
        street_address = address[0].replace(city, "").strip()
        phone = (
            content.find("h5", text=re.compile(r"Phone:.*"))
            .text.replace("Phone: ", "")
            .strip()
        )
        country_code = "US"
        store_number = "<MISSING>"
        hours_of_operation = (
            detail_list[2].text.replace("Hours: ", "").replace(" – ", " - ").strip()
        )
        temp_closed = soup.find("h1", text=re.compile(r"Temporarily Closed"))
        if temp_closed:
            location_type = "TEMP_CLOSED"
        else:
            location_type = "OPEN"
        longitude = "<MISSING>"
        latitude = "<MISSING>"
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
