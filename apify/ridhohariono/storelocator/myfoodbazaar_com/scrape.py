import json
import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "myfoodbazaar.com"
BASE_URL = "https://www.myfoodbazaar.com/"
LOCATION_URL = "https://www.foodbazaar.com/find-your-store/"
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


def parse_json(link_url, js_variable):
    soup = pull_content(link_url)
    pattern = re.compile(r"var\s+" + js_variable + r".*", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    parse = re.search(r"(?s)var\s+" + js_variable + r"\s+=\s+\[(\{.*?\})\]", info)
    data = json.loads("[{}]".format(parse.group(1)))
    return data


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data():
    store_info = parse_json(LOCATION_URL, "locations")
    locations = []
    for row in store_info:
        page_url = LOCATION_URL
        location_name = row["name"]
        if "address2" in row:
            street_address = "{}, {}".format(row["address1"], row["address2"])
        else:
            street_address = row["address1"]
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zipCode"])
        country_code = "US"
        store_number = row["storeNumber"]
        phone = handle_missing(row["phone"])
        location_type = "<MISSING>"
        latitude = handle_missing(row["latitude"])
        longitude = handle_missing(row["longitude"])
        hours_of_operation = row["hourInfo"].replace("7 Days a Week: ", "")
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
