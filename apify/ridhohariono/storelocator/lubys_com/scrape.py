import json
import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

DOMAIN = "lubys.com"
BASE_URL = "https://www.lubys.com"
LOCATION_URL = "https://www.lubys.com/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
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
    soup = bs(session.get(url, headers=HEADERS).content, "html.parser")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_json(page_url):
    soup = pull_content(page_url)
    info = soup.find("script", type="application/ld+json").string
    data = json.loads(info)
    return data


def parse_hours(data):
    results = []
    if data:
        for row in data:
            day = row["dayOfWeek"].split("#", 1)[1]
            hours = row["opens"] + " - " + row["closes"]
            hours_of_operation = "{}: {}".format(day, hours)
            results.append(hours_of_operation)
    return ", ".join(results)


def fetch_store_urls():
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"class": "location-group"})
    links = content.find_all("a", {"class": "location-item"})
    for link in links:
        store_urls.append(BASE_URL + link["href"])
    return store_urls


def fetch_data():
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        data = parse_json(page_url)
        locator_domain = DOMAIN
        location_name = handle_missing(data["name"])
        street_address = handle_missing(data["address"]["streetAddress"])
        city = handle_missing(data["address"]["addressLocality"])
        state = handle_missing(data["address"]["addressRegion"])
        zip_code = handle_missing(data["address"]["postalCode"])
        country_code = "US"
        store_number = "<MISSING>"
        phone = handle_missing(data["telephone"])
        location_type = "<MISSING>"
        latitude = handle_missing(data["geo"]["latitude"])
        longitude = handle_missing(data["geo"]["longitude"])
        hours_of_operation = handle_missing(
            parse_hours(data["openingHoursSpecification"])
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
    data = fetch_data()
    write_output(data)


scrape()
