import re
import json
import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

DOMAIN = "dunnbrothers.com"
BASE_URL = "https://dunnbrothers.com/"
LOCATION_URL = "https://locations.dunnbrothers.com/browse"
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


def fetch_link(link_url, tag, div_class, a_class):
    soup = pull_content(link_url)
    links = []
    for x in soup.find_all(tag, div_class):
        link = x.find("a", a_class)
        if link:
            links.append(link["href"])
    return links


def fetch_store_urls():
    store_urls = []
    state_links = fetch_link(
        LOCATION_URL, "div", {"class": "map-list-item is-single"}, {"class": "ga-link"}
    )
    for state_link in state_links:
        city_links = fetch_link(
            state_link,
            "li",
            {"class": "map-list-item-wrap"},
            {"class": "ga-link"},
        )
        for city_link in city_links:
            store_links = fetch_link(
                city_link,
                "li",
                {"class": "map-list-item-wrap"},
                {"class": "location-name ga-link"},
            )
            for store_link in store_links:
                store_urls.append(store_link)

    return store_urls


def fetch_data():
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        soup = pull_content(page_url)
        info = soup.find("script", type="application/ld+json").string
        data = json.loads(info)[0]
        name = data["name"].split("|")
        locator_domain = DOMAIN
        location_name = handle_missing(data["name"])
        street_address = handle_missing(data["address"]["streetAddress"])
        city = handle_missing(data["address"]["addressLocality"])
        state = handle_missing(data["address"]["addressRegion"])
        zip_code = handle_missing(data["address"]["postalCode"])
        country_code = "US"
        store_number = re.findall(r"\d+", name[1])[0]
        phone = handle_missing(data["address"]["telephone"])
        location_type = "<MISSING>"
        latitude = handle_missing(data["geo"]["latitude"])
        longitude = handle_missing(data["geo"]["longitude"])
        hours_of_operation = handle_missing(data["openingHours"])
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
