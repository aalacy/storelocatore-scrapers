import re
import json
import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "mymdnow.com"
BASE_URL = "https://www.mymdnow.com"
LOCATION_URL = "https://www.mymdnow.com/locations/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
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


def parse_json(link_url, js_variable):
    soup = pull_content(link_url)
    pattern = re.compile(
        r"var\s+" + js_variable + "\\s*=\\s*(\\{.*?\\});", re.MULTILINE | re.DOTALL
    )
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    parse = re.search(r"(?s)var\s+" + js_variable + "\\s*=\\s*(\\{.*?\\});", info)
    data = json.loads(parse.group(1))
    return data


def fetch_data():
    data = parse_json(LOCATION_URL, "map_data")
    store_info = data["offices"]
    locations = []
    for index in store_info:
        store = store_info[index]
        page_url = store["url"]
        locator_domain = DOMAIN
        location_name = handle_missing(store["custom_name"])
        if store["address_2"] and len(store["address_2"]) > 0:
            street_address = "{}, {}".format(store["address_1"], store["address_2"])
        else:
            street_address = store["address_1"]
        city = handle_missing(store["city"])
        state = handle_missing(store["state"])
        zip_code = handle_missing(store["zip"])
        country_code = "US"
        store_number = index
        phone = handle_missing(store["phone"])
        if store["coming_soon"] == "0":
            location_type = "<MISSING>"
        else:
            location_type = "COMING_SOON"
        latitude = handle_missing(store["latitude"])
        longitude = handle_missing(store["longitude"])
        hours_of_operation = handle_missing(store["hours"])
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
