import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re


DOMAIN = "libertybank.com"
BASE_URL = "https://www.libertybank.com"
LOCATION_URL = "https://www.libertybank.net/customer_care/locations/"
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


def parse_hours(table):
    results = []
    if table:
        th = table.find_all("th")
        del th[0]
        opens = table.find_all("tr")[1].find_all("td")
        del opens[0]
        closes = table.find_all("tr")[2].find_all("td")
        del closes[0]
        for i in range(len(opens)):
            hoo = "{}: {} - {}".format(
                th[i].text.strip(), opens[i].text.strip(), closes[i].text
            )
            results.append(hoo)
    return ", ".join(results)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"id": "location-type-2"})
    links = content.find_all("a", text="View Site")
    for link in links:
        store_urls.append(LOCATION_URL + link["href"])
    log.info("Found {} store URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        soup = pull_content(page_url)
        locator_domain = DOMAIN
        location_name = "Liberty Bank"
        content = soup.find("a", {"href": re.compile(r"tel:.*")})
        get_parent = content.parent("p")
        if get_parent:
            address = (
                get_parent[0]
                .get_text(strip=True, separator=",")
                .replace(" - at ", " - at,")
                .replace(" – at ", " – at,")
                .split(",")
            )
            del address[0]
        else:
            address = content.parent.get_text(strip=True, separator=",").split(",")
        street_address = address[0].strip()
        city = address[1].strip()
        state = re.sub(r"\d+", "", address[2].strip())
        zip_code = re.sub(r"\D+", "", address[2].strip())
        country_code = "US"
        store_number = "<MISSING>"
        phone = handle_missing(content.text.strip())
        location_type = "BRANCH"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = parse_hours(
            soup.find("h2", text=re.compile(r"Lobby Hours")).find_next("table")
        )
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
