import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "tjmorris.co.uk"
BASE_URL = "https://storelocator.homebargains.co.uk"
LOCATION_URL = "https://storelocator.homebargains.co.uk/all-stores"
HEADERS = {
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


def parse_hours(data):
    result = re.sub(r"[A-Z],", "y ", data, flags=re.IGNORECASE)
    return result


def fetch_store_urls():
    log.info("Fetching store URL")
    results = []
    soup = pull_content(LOCATION_URL)
    parent = soup.find("table")
    contents = parent.find_all("tr")
    for content in contents:
        td = content.find("td")
        if td:
            hours = content.find("td", {"class": "opening"}).text.strip()
            phone = content.find("td", {"class": "telephone"}).text.strip()
            if "Opening" not in phone and "closed" not in hours:
                link = td.find("a")
                store_locator = {
                    "link": BASE_URL + link["href"],
                    "region": link.text,
                    "phone": phone,
                }
                results.append(store_locator)
    log.info("Found {} store URL ".format(len(results)))
    return results


def fetch_data():
    log.info("Fetching store_locator data")
    store_info = fetch_store_urls()
    locations = []
    for row in store_info:
        page_url = row["link"]
        data = pull_content(page_url)
        content = data.find("div", {"class": "store-detail"})
        locator_domain = DOMAIN
        location_name = handle_missing(
            content.find("h1").get_text(strip=True, separator=" - ")
        )
        address = content.find("p", {"itemprop": "address"}).get_text(
            strip=True, separator=","
        )
        phone = content.find("p", {"class": "telephone"})
        if phone:
            phone = handle_missing(phone.text.strip())
        else:
            phone = "<MISSING>"
        latitude = handle_missing(content.find("span", {"itemprop": "latitude"}).text)
        longitude = handle_missing(content.find("span", {"itemprop": "longitude"}).text)
        split_addr = address.split(",")
        if len(split_addr) < 4:
            street_address = handle_missing(split_addr[0])
            city = handle_missing(split_addr[1])
            state = handle_missing(row["region"])
            zip_code = handle_missing(split_addr[2])
        else:
            street_address = ", ".join(split_addr[:2])
            if len(split_addr) < 5:
                city = handle_missing(split_addr[2])
                state = handle_missing(row["region"])
            else:
                city = handle_missing(split_addr[2])
                state = handle_missing(split_addr[-2])
            zip_code = split_addr[-1]
        country_code = "UK"
        store_number = "<MISSING>"
        get_hours = content.find("div", {"id": "normalOpeningTimes"})
        if get_hours:
            get_hours = get_hours.find("table").get_text(strip=True, separator=",")
            hours_of_operation = handle_missing(parse_hours(get_hours))
        else:
            hours_of_operation = "<MISSING>"
        location_type = "<MISSING>"
        log.info("Append info to locations")
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
