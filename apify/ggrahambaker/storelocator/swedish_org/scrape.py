import csv
import re
import json
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("swedish_org")

session = SgRequests()

headers = {
    "Host": "www.swedish.org",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "connection": "Keep-Alive",
}


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
                "location_type",
                "store_number",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "latitude",
                "longitude",
                "phone",
                "hours_of_operation",
            ]
        )

        # Body
        for row in data:
            writer.writerow(row)


def create_url(loctype):
    return {
        "loctype": loctype,
        "url": f"https://www.swedish.org/locations/list-view?loctype={loctype.replace(' ', '+')}&within=5000",
    }


def fetch_populated_location_map():
    locator_url = "https://www.swedish.org/locations/list-view"
    r = session.get(locator_url, headers=headers)
    groups = fetch_json_data(r.text)

    location_map = {}

    for group in groups:
        latitude = group.get("Latitude", "<MISSING>")
        longitude = group.get("Longitude", "<MISSING>")

        locations = group.get("Locations", [])
        street_address, city, state, zipcode = parse_address(
            group.get("Locations")[0].get("Address")
        )

        for location in locations:
            location_name = location.get("Name").replace("–", "-").split("-")[0].strip()
            if "swedish" not in location_name.split()[0].lower():
                location_name = "Swedish " + location_name
            key = location.get("Maps")
            page_url = f"https://www.swedish.org{key}"

            location_map[location.get("Maps")] = {
                "locator_domain": "swedish.org",
                "page_url": page_url,
                "store_number": "<MISSING>",
                "location_name": location_name,
                "street_address": street_address,
                "city": city,
                "state": state,
                "zip": zipcode,
                "latitude": latitude,
                "longitude": longitude,
                "country_code": "US",
            }

    return location_map


def fetch_loctype_urls():
    locator_url = "https://www.swedish.org/locations"
    r = session.get(locator_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    loctype_options = soup.select("#main_0_contentpanel_1_ddlLocationType option")
    loctypes = [option["value"] for option in loctype_options if option["value"]]

    urls = []
    for loctype in loctypes:
        urls.append(create_url(loctype))

    return urls


def fetch_data():
    location_map = fetch_populated_location_map()

    loctype_urls = fetch_loctype_urls()
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(populate_loc_type, url, location_map)
            for url in loctype_urls
        ]
        for result in as_completed(futures):
            result.result()

    for key, location in location_map.items():
        if not location.get("location_type"):
            location_map[key]["location_type"] = "<MISSING>"

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(populate_details, location, location_map)
            for location in location_map.items()
        ]
        for result in as_completed(futures):
            location = result.result()

            yield [
                location.get("locator_domain"),
                location.get("page_url"),
                location.get("location_name"),
                location.get("location_type"),
                location.get("store_number"),
                location.get("street_address"),
                location.get("city"),
                location.get("state"),
                location.get("zip"),
                location.get("country_code"),
                location.get("latitude"),
                location.get("longitude"),
                location.get("phone"),
                location.get("hours_of_operation"),
            ]


def populate_loc_type(loctype_url, location_map):
    r = session.get(loctype_url.get("url"), headers=headers)
    groups = fetch_json_data(r.text)

    for group in groups:
        for location in group.get("Locations", []):
            key = location.get("Maps")

            if key in location_map:
                location_map[key]["location_type"] = loctype_url.get("loctype").replace(
                    "swedish", ""
                )
            else:
                logger.info(f"location missing in map: {key}")


def fetch_json_data(content):
    match = re.search(r"locationsList\s*=\s*[\'|\"](.*?)[\'|\"];", content)
    data = json.loads(match.group(1))
    return data


def parse_address(address):
    if address == "":
        return ["<MISSING>", "<MISSING>", "<MISSING>", "<MISSING>"]

    parts = address.split("<br/>")
    city_state_zip = parts.pop(-1)
    city_state_zip_parts = city_state_zip.split(", ")

    if len(city_state_zip_parts) == 2:
        city, state_zip = city_state_zip_parts
        state, zipcode = state_zip.split(" ")
    else:
        state = "<MISSING>"
        city, zipcode = city_state_zip_parts[0].split(" ")

    street_address = " ".join(parts).strip()
    return [street_address, city, state, zipcode[0:5]]


def populate_details(location_tuple, location_map):
    key, location = location_tuple

    r = session.get(location.get("page_url"))
    soup = BeautifulSoup(r.text, "html.parser")

    phone = soup.find(class_="mobile-only-phone")

    phoneNumber = clean_phone(phone)
    if not phoneNumber:
        try:
            phoneNumber = re.findall(
                r"[\d]{3}-[\d]{3}-[\d]{4}", str(soup.find(id="main-content").text)
            )[0]
        except:
            pass

    hours = soup.select_one("#main_0_rightpanel_0_pnlOfficeHours .option-content")
    hours_of_operation = (
        hours.text.replace("\n", " ").strip() if hours and hours.text != "" else None
    )

    location_map[key]["phone"] = phoneNumber or "<MISSING>"
    location_map[key]["hours_of_operation"] = hours_of_operation or "<MISSING>"

    return location_map[key]


def clean_phone(phone):
    if not phone or "-" not in phone.text:
        return None

    phoneNumber = phone.text.strip()
    if " (" in phoneNumber:
        phoneNumber = phoneNumber.split(" (")[1][:-1].strip()

    return phoneNumber


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
