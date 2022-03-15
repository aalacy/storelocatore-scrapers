import csv
import json
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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


def fetch_data():
    # Your scraper here
    session = SgRequests(proxy_rotation_failure_threshold=0).requests_retry_session(
        retries=0, backoff_factor=0.3
    )

    items = []
    scraped_items = []

    DOMAIN = "cashstore.com"
    start_url = (
        "https://www.cashstore.com/api/v1/stores/search?latitude={}&longitude={}"
    )

    all_locations = []
    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=50
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng))
        all_locations += json.loads(response.text)

    for poi in all_locations:
        store_url = urljoin("https://www.cashstore.com", poi["url"])
        store_url = store_url if store_url else "<MISSING>"
        location_name = "Cash Store"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["storeNumber"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["isClosed"]:
            location_type = "closed"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days:
            opens = poi[f"{day}Open"]
            closes = poi[f"{day}Close"]
            hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            DOMAIN,
            store_url,
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
