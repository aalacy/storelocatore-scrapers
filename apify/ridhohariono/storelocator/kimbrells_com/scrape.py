import re
import json
import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "kimbrells.com"
BASE_URL = "http://kimbrells.com/"
LOCATION_URL = "http://kimbrells.com/allshops"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def write_output(data):
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


def parse_phone(element):
    phone_pattren = r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"
    get_phone = element.find(text=re.compile(phone_pattren))
    return get_phone


def parse_hours(element):
    hours = (
        element.find("p")
        .get_text(strip=True, separator=",")
        .replace("\xa0", " ")
        .split(",")
    )
    pattern = r",Closed:\s+.*\d{1,2}/\d{2}/\d{2,4}"
    hours_of_operation = re.sub(pattern, "", ",".join(hours[4:])).strip()
    return hours_of_operation


def parse_address(element):
    address = element.find("p").get_text(strip=True, separator=",").split(",")
    return {
        "street": address[0].strip(),
        "city": address[1].strip(),
        "state": address[2].strip().split(" ")[0],
        "zip_code": address[2].strip().split(" ")[1],
    }


def parse_json(data):
    results = json.loads(data)
    return results


def fetch_data():
    soup = pull_content(LOCATION_URL)
    data = soup.find("input", {"class": "shop-resources"})
    store_info = parse_json(data["data-markersdata"])
    locations = []
    for row in store_info:
        page_url = LOCATION_URL
        locator_domain = DOMAIN
        location_name = handle_missing(row["Name"])
        soup = bs(row["MarkerDescription"], "lxml")
        address = parse_address(soup)
        street_address = handle_missing(address["street"])
        city = handle_missing(address["city"])
        state = handle_missing(address["state"])
        zip_code = handle_missing(address["zip_code"])
        country_code = "US"
        store_number = handle_missing(row["Id"])
        phone = handle_missing(parse_phone(soup))
        location_type = "<MISSING>"
        latitude = handle_missing(row["Latitude"])
        longitude = handle_missing(row["Longitude"])
        hours_of_operation = handle_missing(parse_hours(soup))
        log.info(
            "Append info to locations: {} : {}".format(location_name, street_address)
        )
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
