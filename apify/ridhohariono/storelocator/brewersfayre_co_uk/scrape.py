import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "brewersfayre.co.uk"
BASE_URL = "https://www.brewersfayre.co.uk"
LOCATION_URL = "https://www.brewersfayre.co.uk/en-gb/locations"
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
    content = soup.find("div", {"class": "pagecatalogue"})
    links = content.find_all("a", {"class": "title-text"})
    for link in links:
        store_urls.append(BASE_URL + link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        soup = pull_content(page_url)
        content = soup.find("div", {"class": "dynherolocationdetails"})
        locator_domain = DOMAIN
        location_name = handle_missing(
            content.find(
                "h1", {"class": "h1 title-text brand-header light"}
            ).text.strip()
        )
        address = content.find("address").get_text(strip=True, separator=",").split(",")
        if len(address) > 4:
            street_address = ",".join(address[:2])
            city = handle_missing(address[2])
            state = handle_missing(address[3])
            zip_code = handle_missing(address[4])
        elif len(address) == 4:
            street_address = address[0]
            city = handle_missing(address[1])
            state = handle_missing(address[2])
            zip_code = handle_missing(address[3])
        elif len(address) < 4:
            street_address = address[0]
            city = handle_missing(address[1])
            state = handle_missing(address[1])
            zip_code = handle_missing(address[2])
        country_code = "UK"
        store_number = "<MISSING>"
        phone = handle_missing(
            content.find(
                "a", {"class": "details--table-cell__phone icon__phone"}
            ).text.strip()
        )
        check_status = session.get(
            page_url + ".locationannouncement.json", headers=HEADERS
        ).json()
        hoo_content = content.find("p", text="Opening times").find_parent("div")
        hoo = hoo_content.find_all("p")
        hoo.pop(0)
        if check_status["show"] and "CLOSED" in check_status["message"]:
            location_type = "TEMP_CLOSED"
            hours_of_operation = ", ".join([x.text.strip() for x in hoo[:2]])
        elif "CLOSED" in hoo_content.text.strip(","):
            location_type = "TEMP_CLOSED"
            hours_of_operation = "<MISSING>"
        elif "In line with the latest government" in hoo_content.text.strip(","):
            location_type = "OPEN"
            hours_of_operation = re.sub(
                r".*restrictions\s+", "", hoo[0].text.replace(".", "")
            )
        else:
            location_type = "OPEN"
            hours_of_operation = ", ".join([x.text.strip() for x in hoo[:2]])
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
