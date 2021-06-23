import csv
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.static import (
    static_coordinate_list,
    SearchableCountries,
)
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("walgreens_com__pharmacy")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for rows in data:
            writer.writerows(rows)


search = static_coordinate_list(10, SearchableCountries.USA)
session = SgRequests()


@retry(stop=stop_after_attempt(3), reraise=True)
def fetch(url):
    return session.get(url).text


@retry(stop=stop_after_attempt(3), reraise=True)
def fetch_page(coord):
    lat, lng = coord
    url = "https://www.walgreens.com/locator/v1/stores/search?requestor=search"
    payload = {
        "r": "50",
        "requestType": "dotcom",
        "s": "20",
        "p": 1,
        "lat": lat,
        "lng": lng,
    }
    return session.post(url, json=payload).json()


def fetch_locations(coord, ids):
    data = fetch_page(coord)
    website = "walgreens.com/pharmacy"

    locations = []
    if not data.get("results"):
        return locations

    for item in data["results"]:
        store = item["storeSeoUrl"].split("/id=")[1]
        if store in ids:
            continue
        ids.append(store)

        loc = "https://www.walgreens.com" + item["storeSeoUrl"]
        lat = item["latitude"]
        country = "US"
        lng = item["longitude"]
        add = item["store"]["address"]["street"]
        zc = item["store"]["address"]["zip"]
        city = item["store"]["address"]["city"]
        state = item["store"]["address"]["state"]
        name = item["store"]["name"]
        phone = (
            item["store"]["phone"]["areaCode"].strip()
            + item["store"]["phone"]["number"].strip()
        )
        typ = "<MISSING>"
        try:
            hours_of_operation = get_hours(loc)
        except Exception as e:
            logger.error(f"{store} >>> {e}")
            hours_of_operation = "<MISSING>"

        locations.append(
            [
                website,
                loc,
                name,
                add,
                city,
                state,
                zc,
                country,
                store,
                phone,
                typ,
                lat,
                lng,
                hours_of_operation,
            ]
        )

    return locations


def get_hours(url):
    page = fetch(url)
    soup = BeautifulSoup(page, "html.parser")
    script = soup.select_one("#jsonLD")

    if not script:
        return "<MISSING>"

    hours_of_operation = []
    data = json.loads(script.string)
    hours = data["openingHoursSpecification"]

    for hour in hours:
        day = hour["dayOfWeek"].split(" ").pop(0)
        opens = hour["opens"]
        closes = hour["closes"]

        hours_of_operation.append(f"{day}: {opens}-{closes}")

    return (",").join(hours_of_operation) or "<MISSING>"


def fetch_data():
    ids = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_locations, coord, ids) for coord in search]
        for future in as_completed(futures):
            locations = future.result()
            yield locations


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
