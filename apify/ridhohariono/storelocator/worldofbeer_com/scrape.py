import re
import json
import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "worldofbeer.com"
BASE_URL = "https://worldofbeer.com"
LOCATION_URL = "https://worldofbeer.com/locations/"
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


def get_hours(page_url):
    soup = pull_content(page_url)
    hours = soup.find("p", {"class": "hours"}).get_text(strip=True, separator=",")
    check_hours_exist = re.search(r".*\d{1,2}(am|pm)(.*?)", hours)
    if not check_hours_exist:
        hours_of_operation = "<MISSING>"
    else:
        hours_of_operation = hours

    return hours_of_operation


def fetch_data():
    data = parse_json(LOCATION_URL, "site_info")
    store_info = json.loads(data["locations"])
    locations = []
    for row in store_info:
        page_url = row["permalink"]
        locator_domain = DOMAIN
        location_name = handle_missing(row["title"])
        street_address = handle_missing(row["address"])
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zip"])
        country_code = "US"
        store_number = handle_missing(row["id"])
        phone = handle_missing(row["phone"])
        location_type = "<MISSING>"
        lat_long = row["latitude_longitude"].split(";")
        latitude = handle_missing(lat_long[0])
        longitude = handle_missing(lat_long[1])
        hours_of_operation = get_hours(page_url)
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
