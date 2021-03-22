import re
import csv
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "jinya-ramenbar.com"
BASE_URL = "https://jinya-ramenbar.com"
LOCATION_URL = "http://jinya-ramenbar.com/locations/"
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
    return field.strip()


def parse_json(soup, js_variable):
    pattern = re.compile(r"var\s+" + js_variable)
    script = soup.find("script", text=pattern)
    if script:
        parse = re.search(
            r".*data\.push\((.*)\).*//Markers", script.string, re.MULTILINE | re.DOTALL
        ).group(1)
    else:
        return False
    parse = (
        parse.replace("//Latitude", "")
        .replace("//URL", "")
        .replace("//longitude", "")
        .replace("lat", '"lat"')
        .replace("lng", '"lng"')
        .replace("url", '"url"')
    )
    parse = re.sub(r"\s+", "", parse).replace("'", '"')
    parse = re.sub(r",$", "", parse)
    data = json.loads("[" + parse + "]")
    return data


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    lat_long = parse_json(soup, "latlng")
    stores = soup.find_all(
        "a",
        {
            "class": "loc_btn btn",
            "href": re.compile(r"https\:\/\/www\.jinyaramenbar\.com\/locations\/"),
        },
    )
    for store in stores:
        link = store["href"]
        if "tustin-2/" not in link:
            for val in lat_long:
                if val["url"] == link:
                    data = {"url": link, "lat": val["lat"], "lng": val["lng"]}
                    store_urls.append(data)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def parse_hoo(address, phone):
    unused = ["Opening", "Temporarily", "ANNOUNCEMENT", "NOW OPEN"]
    hoo = ", ".join(address[3:])
    hoo = hoo.replace("/, ", "").replace(phone, "")
    hoo = re.sub(r"\d{3}\-\d{3}\-\d{4},", "", hoo).strip()
    for x in unused:
        if x in hoo:
            hoo = re.sub(x + ".*", "", hoo)
    hoo = re.sub(r", $", "", hoo).strip()
    return hoo


def get_address(address, city):
    street_address = handle_missing(
        re.sub(
            city + ".*",
            "",
            address,
            flags=re.IGNORECASE,
        )
    )
    return street_address


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for store in store_urls:
        page_url = store["url"]
        soup = pull_content(page_url)
        row = soup.find("div", {"id": "main_contents"})
        locator_domain = DOMAIN
        location_name = handle_missing(row.find("h1").text.strip())
        address = (
            row.find("div", {"class": "loc_details"})
            .get_text(strip=True, separator=",")
            .split(",")
        )
        location_type = "OPEN"
        if "(Coming Soon)" in location_name:
            location_name = location_name.replace("(Coming Soon)", "")
            location_type = "COMING_SOON"
        if "Downtown LA" in location_name:
            city = "Los Angeles"
        elif "Washington DC" in location_name:
            city = "Washington"
            state = "Washington DC"
            zip_code = handle_missing(address[1].strip().replace("DC", ""))
        else:
            city = handle_missing(location_name.split("|")[0].strip())
            state = handle_missing(address[1].strip()[:2])
            zip_code = handle_missing(address[1].strip().replace(state, ""))
        street_address = get_address(address[0], city)
        country_code = "US" if len(zip_code) <= 5 else "CA"
        store_number = "<MISSING>"
        if len(address) > 2:
            phone = handle_missing(address[2])
            if len(address) >= 4:
                hours_of_operation = parse_hoo(address, phone)
            else:
                hours_of_operation = "<MISSING>"
        else:
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"
        latitude = handle_missing(store["lat"])
        longitude = handle_missing(store["lng"])
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
