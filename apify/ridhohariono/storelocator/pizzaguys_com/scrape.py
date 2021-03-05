import re
import json
import csv
import usaddress
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests

DOMAIN = "pizzaguys.com"
BASE_URL = "https://www.pizzaguys.com"
LOCATION_URL = "https://www.pizzaguys.com/locations/"
HEADERS = {
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


def parse_hours(hour_elements):
    hours = []
    for row in hour_elements:
        hours.append(handle_missing(row.get_text(strip=True, separator=" ")))

    return hours


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


def get_address(soup, soup_addr):
    address = soup.find("h2", {"class": "location-contact-title"})
    if len(address) > 0:
        address = address.get_text(strip=True, separator=",")
    else:
        address = soup_addr.find("p", {"class": "address"})
        if address:
            address = address.get_text(strip=True, separator=",")
        else:
            address = soup_addr.find("p")
            address = address.get_text(strip=True, separator=",")
    return address


def fetch_store_urls(link_url):
    data = parse_json(link_url, "maplistScriptParamsKo")
    store_info = {}
    results = []
    for x in data["KOObject"][0]["locations"]:
        soup = bs(x["description"], "html.parser")
        content = soup.find_all("div", {"class": "fusion-button-wrapper"})
        if content:
            store_number = content[0].find("a")
            link = content[1].find("a")
            if link:
                href = link["href"]
                if BASE_URL not in link:
                    href = BASE_URL + link["href"]
                if "location" not in link["href"]:
                    href = LOCATION_URL + link["href"]
                store_number_url_parsed = urlparse(BASE_URL + store_number["href"])
                store_number = parse_qs(store_number_url_parsed.query)["store"][0]
                store_info = {
                    "title": x["title"],
                    "store_number": store_number,
                    "link": href,
                    "latitude": x["latitude"],
                    "longitude": x["longitude"],
                }
                results.append(store_info)
    return results


def fetch_data():
    store_info = fetch_store_urls(LOCATION_URL)
    locations = []
    for row in store_info:
        page_url = row["link"]
        soup = pull_content(page_url)
        info = parse_json(page_url, "maplistFrontScriptParams")
        data = json.loads(info["location"])
        if data:
            locator_domain = DOMAIN
            location_name = handle_missing(row["title"])
            soup_addr = bs(data["description"], "html.parser")
            address = get_address(soup, soup_addr)
            parse_street = address.split(",")
            if len(parse_street) == 4:
                street_address = ",".join(parse_street[:2])
            else:
                street_address = parse_street[0]
            parse_addr = usaddress.tag(address)
            city = handle_missing(parse_addr[0]["PlaceName"])
            state = handle_missing(parse_addr[0]["StateName"])
            zip_code = handle_missing(parse_addr[0]["ZipCode"])
            country_code = "US"
            store_number = row["store_number"]
            phone = handle_missing(soup.find("p", {"class": "call-now"})).text
            location_type = "<MISSING>"
            latitude = handle_missing(row["latitude"])
            longitude = handle_missing(row["longitude"])
            parsed_hours = parse_hours(soup.find_all("li", {"class": "hours-item"}))
            hours_of_operation = handle_missing(",".join(parsed_hours))
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
