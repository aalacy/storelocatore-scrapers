import json
import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "gonavis.com"
BASE_URL = "https://www.gonavis.com"
LOCATION_URL = "https://www.gonavis.com/search"
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
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return 404
    soup = bs(req.content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def is_duplicate(list, filter):
    for x in list:
        if filter in x:
            return True
    return False


def get_lat_long(soup):
    pattern = re.compile(
        r"jQuery\.extend\(Drupal\.settings,\{.*?\}\)", re.MULTILINE | re.DOTALL
    )
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("<!--//--><![CDATA[//><!--", "").replace(
            "//--><!]]>", ""
        )
    else:
        return False
    parse = re.search(r"\"features\":\[\{.*?\}\]", info)
    if parse:
        data = json.loads(parse.group().replace('"features":', ""))
    else:
        return False
    return data[0]


def parse_hours(hours):
    if not any(char.isdigit() for char in hours):
        return "<MISSING>"
    return hours


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"id": "view_content"})
    details = []
    links = content.find_all("a", {"style": "text-decoration:underline;"})
    for link in links:
        info = link.parent.find_previous_sibling("div").get_text(
            strip=True, separator=","
        )
        result = {BASE_URL + link["href"]: info}
        details.append(result)
        store_urls.append(BASE_URL + link["href"])
    data = list(set(store_urls))
    log.info("Found {} store URL ".format(len(data)))
    return {"link": data, "details": details}


def fetch_data():
    log.info("Fetching store_locator data")
    store_info = fetch_store_urls()
    locations = []
    for page_url in store_info["link"]:
        locator_domain = DOMAIN
        data = pull_content(page_url)
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        if data == 404:
            for row in store_info["details"]:
                if page_url in row:
                    details = row[page_url].split(",")
                    location_name = details[1].strip()
                    street_address = details[0].strip()
                    city = details[1].strip()
                    state = details[2].strip()
                    phone = details[3].strip()
                    zip_code = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    hours_of_operation = "<MISSING>"
        else:
            container = (
                data.find("div", {"class": "main-container"})
                .find("div", {"class": "views-content"})
                .find("div", {"class": "col-md-4 col-md-pull-8"})
            )
            if not container:
                continue
            get_content = container.find_all("div", {"class": "panel panel-default"})
            if len(get_content) < 8:
                content = get_content[1]
            elif len(get_content) == 8:
                content = get_content[2]
            else:
                content = get_content[3]
            location_name = handle_missing(
                content.find("h3", {"class": "panel-title"}).text.strip()
            )
            address = content.find("ul", {"class": "list-group"}).find("li")
            address_details = address.find("div", {"style": "margin-left:25px;"})
            street_address = handle_missing(
                address.find("i", {"class": "fa fa-map-marker"}).next_sibling
            )
            city = handle_missing(address_details.text.split(",")[0])
            state = handle_missing(
                address_details.text.split(",")[1].strip().split(" ")[0]
            )
            zip_code = handle_missing(
                address_details.text.split(",")[1].replace(state, "").strip()
            )
            phone = content.find("i", {"class": "fa fa-phone"}).next_sibling.text
            location_type = "<MISSING>"
            hours_of_operation = parse_hours(
                content.find("i", {"class": "fa fa-clock-o"}).next_sibling
            )
            lat_long = get_lat_long(data)
            if lat_long:
                latitude = lat_long["lat"]
                longitude = lat_long["lon"]
            else:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            log.info(
                "Append info to locations => {}:{} => {}".format(
                    latitude, longitude, street_address
                )
            )
            if is_duplicate(locations, latitude):
                log.info(
                    "Found duplicate => {}:{} => {}".format(
                        latitude, longitude, street_address
                    )
                )
                continue
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
