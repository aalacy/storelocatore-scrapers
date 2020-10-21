import re
import csv
import time
from sgzip import coords_for_radius
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

session = SgRequests()
MISSING = "<MISSING>"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
}

POI_FIELDS = [
    "locator_domain",
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
    "page_url",
]


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(POI_FIELDS)
        # Body
        for row in data:
            writer.writerow(row)


def fetch_location_hours(location):
    response = session.get(location.get("page_url"), headers=headers)
    soup = BeautifulSoup(response.text, features="lxml")

    hours = soup.select(
        ".ps-properties-property__info__hours__section:first-child .ps-properties-property__cleanlist-item"
    )

    hours_of_operation = [hour.getText().strip() for hour in hours]
    location["hours_of_operation"] = ",".join(hours_of_operation)

    record = [location[field] for field in POI_FIELDS]
    return record


def fetch_data():
    MAX_COUNT = 3000
    MAX_DISTANCE = 200
    MAX_WORKERS = 8

    location_map = {}

    locator_domain = "publicstorage.com"
    coords = coords_for_radius(MAX_DISTANCE)

    for coord in coords:
        params = {
            "lat": coord[0],
            "lng": coord[1],
            "maximumSites": MAX_COUNT,
            "radius": MAX_DISTANCE,
            "isgeo": True,
        }

        location_url = (
            f"https://www.publicstorage.com/api/sitecore/HomeLanding/GetNearbyLocations"
        )
        data = session.get(location_url, headers=headers, params=params).json()
        locations = data.get("Result", [])

        for location in locations:
            store_number = location.get("SiteID", MISSING)
            if store_number in location_map:
                continue

            url = location.get("Url")
            page_url = f"https://www.publicstorage.com{url}" if url else MISSING

            address = location.get("FormattedAddress", "")
            cleaned_address = re.sub("\s\s+", " ", address)

            location_name = (
                f"Public Storage Self-Storage Units at {cleaned_address}"
                if cleaned_address
                else MISSING
            )

            phone = location.get("PhoneNumber", MISSING).strip()

            street_address = location.get("Street1", MISSING).strip()
            city = location.get("City", MISSING).strip()
            state = location.get("StateCode", MISSING).strip()

            postal = location.get("PostalCode", MISSING).strip()
            country_code = "US"
            lat = location.get("Latitude", MISSING)
            lng = location.get("Longitude", MISSING)

            location_type = MISSING

            record = {
                "locator_domain": locator_domain,
                "location_name": location_name,
                "street_address": street_address,
                "city": city,
                "state": state,
                "zip": postal,
                "country_code": country_code,
                "store_number": store_number,
                "phone": phone,
                "location_type": location_type,
                "latitude": lat,
                "longitude": lng,
                "page_url": page_url,
            }

            location_map[store_number] = record

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(fetch_location_hours, location)
            for store_number, location in location_map.items()
        ]

        for job in as_completed(futures):
            data = job.result()
            yield data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    start_time = time.time()
    scrape()
    print(f"{time.time() - start_time} seconds")
