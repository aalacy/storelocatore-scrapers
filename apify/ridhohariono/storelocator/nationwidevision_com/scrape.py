import json
import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "nationwidevision.com"
BASE_URL = "https://nationwidevision.com"
LOCATION_URL = "https://nationwidevision.com/locations/list"
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


def parse_json(page_url):
    log.info("Parse content to json => " + page_url)
    soup = pull_content(page_url)
    info = soup.find("script", type="application/ld+json").string
    data = json.loads(info)
    return data


def parse_hours(data):
    log.info("Reformat hours hours_of_operation")
    hours = data.replace(" am", " am ").replace("-", "- ").replace("pm", "pm,")
    return hours


def fetch_store_urls():
    log.info("Fetching store URL")
    results = []
    store_info = {}
    soup = pull_content(LOCATION_URL)
    parent = soup.find("div", {"class": re.compile("js-view-dom-id-.*")})
    contents = parent.find_all("div", {"class": "views-row"})
    for content in contents:
        title = content.find("div", {"class": "views-field-title"}).get_text(strip=True)
        store_number = content.find(
            "div", {"class": "views-field-field-store-number"}
        ).text
        content_addr = content.find("p", {"class": "address"})
        get_address = content_addr.find_all(
            "span", {"class": re.compile("address-line.*")}
        )
        street_address = ", ".join([addr.get_text(strip=True) for addr in get_address])
        city = content_addr.find("span", {"class": "locality"}).text
        state = content_addr.find("span", {"class": "administrative-area"}).text
        zip_code = content_addr.find("span", {"class": "postal-code"}).text
        country = content_addr.find("span", {"class": "country"}).text
        store_link = content.find("div", {"class": "views-field-title"}).find("a")[
            "href"
        ]
        store_info = {
            "title": title,
            "store_number": store_number,
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip_code": zip_code,
            "country": country,
            "link": BASE_URL + store_link,
        }
        results.append(store_info)
    log.info("Found {} store URL ".format(len(results)))
    return results


def fetch_data():
    log.info("Fetching store_locator data")
    store_info = fetch_store_urls()
    locations = []
    for row in store_info:
        page_url = row["link"]
        data = pull_content(page_url)
        subtitle = data.find("h2", {"class": "location--subtitle"})
        if subtitle and "Permanently Closed" in subtitle.text.strip():
            continue
        geo_content = data.find("div", {"class": re.compile(".*-map")})
        store_content = data.find("div", {"class": re.compile(".*-detail")})
        lat_long = geo_content.find("h2", {"class": "location-title"}).text.split(",")
        latitude = handle_missing(lat_long[0])
        longitude = handle_missing(lat_long[1])
        get_hours = store_content.find("div", {"class": "office-hours"}).get_text(
            strip=True, separator=" "
        )
        hours_of_operation = handle_missing(parse_hours(get_hours))
        locator_domain = DOMAIN
        location_name = handle_missing(row["title"])
        street_address = handle_missing(row["street_address"])
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zip_code"])
        country_code = "US"
        store_number = handle_missing(row["store_number"])
        phone = store_content.find("p", {"class": "tel"})
        if phone:
            phone = handle_missing(phone.get_text(strip=True))
        else:
            phone = "<MISSING>"
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
