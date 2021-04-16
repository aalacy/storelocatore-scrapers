import csv
import re
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "chuckanddons.com"
BASE_URL = "https://chuckanddons.com"
LOCATION_URL = "https://chuckanddons.com/stores/"
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
    pattern = re.compile(r"var\s+" + js_variable + r"\s+=.*", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    parse = re.search(r"(?s)var\s+" + js_variable + r"\s+=\s+'\[\{.*?\}\]'", info)
    parse = parse.group().replace("var markers = '", "").replace("]'", "]")
    data = json.loads(parse)
    return data


def parse_hours(element):
    hoo = (
        element.find("div", {"class": "hours"})
        .find("p")
        .get_text(strip=True, separator=",")
        .replace("Hours", "")
        .replace("\r", ",")
        .replace("\n", "")
    )
    hoo = re.sub(r"Pet Wash closes .*", "", hoo)
    hoo = re.sub(r"Chuck & Don's.*", "", hoo)
    hoo = re.sub(r"Holiday.*", "", hoo)
    hoo = re.sub(r",$", "", hoo).strip()
    return hoo


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("section", {"class": "search-results"}).find(
        "div", {"class": "search-results__body"}
    )
    stores = content.find_all("div", {"class": "search-results__store"})
    for store in stores:
        link = store.find("a", {"class": "store--location__link"})
        address_phone = store.find("section", {"class": "store-address"}).get_text(
            strip=True, separator=","
        )
        hoo = store.find("div", {"class": "store-opening-time"}).get_text(
            strip=True, separator=" "
        )
        store_dict = {
            "title": link.text.strip(),
            "link": BASE_URL + link["href"],
            "store_number": link["data-store-number"],
            "address_phone": address_phone,
            "hoo": hoo,
        }
        store_urls.append(store_dict)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    lat_long = parse_json(soup, "markers")
    store_content = soup.find_all("div", {"class": "store-container"})
    locations = []
    i = 0
    for row in store_content:
        page_url = row.find("h3", {"class": "store-name"}).find("a")["href"]
        locator_domain = DOMAIN
        location_name = handle_missing(
            row.find("h3", {"class": "store-name"}).text.strip()
        )
        address = (
            row.find("div", {"class": "address"})
            .get_text(strip=True, separator=",")
            .split(",")
        )
        if len(address) == 4:
            street_address = ", ".join(address[:2]).strip()
            city = handle_missing(address[2].strip())
            state = re.sub(r"\d+", "", address[3]).strip()
            zip_code = re.sub(r"\D", "", address[3]).strip()
        elif len(address) < 4:
            street_address = address[0].strip()
            city = handle_missing(address[1].strip())
            state = re.sub(r"\d+", "", address[2]).strip()
            zip_code = re.sub(r"\D", "", address[2]).strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = row.find("div", {"class": "contact"}).text.strip().replace("Tel: ", "")
        location_type = "<MISSING>"
        hours_of_operation = handle_missing(parse_hours(row))
        latitude = handle_missing(lat_long[i]["lat"])
        longitude = handle_missing(lat_long[i]["lng"])
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
        i += 1
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
