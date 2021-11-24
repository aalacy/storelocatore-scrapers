import json
import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "fitnessevolution.com"
BASE_URL = "https://www.fitnessevolution.com"
LOCATION_URL = "https://fitnessevolution.com/locations/"
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


def parse_json(link_url):
    soup = pull_content(link_url)
    pattern = re.compile(r"var\s+wtr_google_maps.*", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    json_content = re.search(
        r"(?s)var\s+wtr_google_maps\s+=\s+\{\}\;wtr_google_maps\[\s+0\s+\]\s+=\s+(\{.*\})",
        info,
    )
    parse = re.search(
        r"(?s)\.markers\[\s*0\s*\]\s+=\s+(\{.*\})",
        json_content.group(1),
    )
    content = re.sub(
        r"\b(title_marker|url_link?|marker_style|own_marker_style|geo_marker|width|height|url)\s+:",
        r'"\1":',
        parse.group(1),
    )
    data = {"soup": soup, "info": json.loads(content)}
    return data


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find(
        "div",
        {"class": "wtrPageContent vcRow wtrMargin clearfix"},
    )
    links = content.find_all("a")
    for link in links:
        store_urls.append(link["href"])
    log.info("Found {} store URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    excpet_page = "https://fitnessevolution.com/clubs/silver-spring-maryland/"
    if excpet_page in page_urls:
        page_urls.remove(excpet_page)
    locations = []
    for page_url in page_urls:
        data = parse_json(page_url)
        soup = data["soup"]
        locator_domain = DOMAIN
        location_name = (
            soup.find_all("meta", {"property": "og:title"})[1]["content"]
            .split(",")[0]
            .strip()
        )
        address = data["info"]["title_marker"].split(",")
        if len(address) > 3:
            street_address = "{},{}".format(address[0], address[1]).strip()
            city = address[2].strip()
            state = re.sub(r"\d+", "", address[3]).strip()
            zip_code = re.sub(r"\D+", "", address[3]).strip()
        else:
            street_address = address[0].strip()
            city = address[1].strip()
            state = re.sub(r"\d+", "", address[2]).strip()
            zip_code = re.sub(r"\D+", "", address[2]).strip()
        street_address = street_address.replace(
            "Royal Plaza Shopping Center,", ""
        ).strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = soup.find(
            "h3", {"style": "text-align: center; color: white;"}
        ).text.strip()
        location_type = "fitnessevolution"
        latlong = data["info"]["geo_marker"].split("|")
        latitude = latlong[0]
        longitude = latlong[1]
        hours_of_operation = "<MISSING>"
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
