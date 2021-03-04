import csv
import json
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "traction.com"
    start_url = "https://www.traction.com/en/store-finder?q={}&page=0"

    session.get(start_url)
    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], max_radius_miles=200
    )
    for code in all_codes:
        code_url = start_url.format(code + "%201J4")
        response = session.get(code_url)
        try:
            data = json.loads(response.text)
        except Exception:
            continue
        all_locations += data["data"]
        if data["total"] > 10:
            total_pages = data["total"] // 10 + 1
            for page in range(1, total_pages):
                page_url = add_or_replace_parameter(code_url, "page", str(page))
                response = session.get(page_url)
                try:
                    data = json.loads(response.text)
                    all_locations += data["data"]
                except Exception:
                    continue

    for poi in all_locations:
        store_url = (
            urljoin(start_url, poi["url"])
            .split("?")[0]
            .replace(" ", "-")
            .replace("(", "")
            .replace(")", "")
            .replace(".", "")
        )
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["town"]
        city = city if city else "<MISSING>"
        state = poi["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "CA"
        store_number = poi["storeId"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for day, hours in poi["openings"].items():
            hoo.append(f"{day} {hours}")
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
