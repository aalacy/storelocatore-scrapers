import csv
import re
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "gailsbread.co.uk"
BASE_URL = "https://www.gailsbread.co.uk"
LOCATION_URL = "https://gailsbread.co.uk/find-us/"
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


def parse_json(soup, js_variable):
    pattern = re.compile(
        r"var\s+" + js_variable + r"\s+= \{.*?\}", re.MULTILINE | re.DOTALL
    )
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    parse = re.search(r"\"locations\"\:(\[\{.*?\}\])", info)
    parse = parse.group(1)
    data = json.loads(parse)
    return data[0]


def parse_hours(table):
    if not table:
        return "<MISSING>"
    hoo = table.get_text(strip=True, separator=",").replace("day,", "day: ")
    return hoo


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"id": "custom-wpsl-shops-details-list"}).find("ul")
    stores = content.find_all("li")
    for store in stores:
        link = store.find("a")
        store_urls.append(link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        info = parse_json(soup, "wpslMap_0")
        locator_domain = DOMAIN
        location_name = handle_missing(info["store"]).replace("&#8217;", "'")
        if len(info["address2"]) > 0:
            street_address = "{}, {}".format(info["address"], info["address2"])
        else:
            street_address = info["address"]
        city = handle_missing(info["city"])
        state = handle_missing(info["state"])
        zip_code = handle_missing(info["zip"])
        country_code = "UK"
        store_number = info["id"]
        get_phone = handle_missing(soup.find("a", {"href": re.compile(r"tel:\d+")}))
        if get_phone != "<MISSING>":
            phone = get_phone.text.strip()
        hours_of_operation = parse_hours(
            soup.find("table", {"class": "wpsl-opening-hours"})
        )
        location_type = "<MISSING>"
        latitude = handle_missing(info["lat"])
        longitude = handle_missing(info["lng"])
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
