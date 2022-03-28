import csv
import json
from w3lib.url import add_or_replace_parameter
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgrequests import SgRequests


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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "jared.com"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=50,
        max_search_results=None,
    )

    all_locations = []
    for code in all_codes:
        url = "https://www.jared.com/store-finder/find?q={}&page=0".format(code)
        response = session.get(url)
        data = json.loads(response.text)
        if not data.get("data"):
            continue
        all_locations += data["data"]
        if data["total"] > 5:
            for page in range(1, data["total"] // 5 + 2):
                page_url = add_or_replace_parameter(url, "page", str(page))
                response = session.get(page_url)
                data = json.loads(response.text)
                if not data.get("data"):
                    continue
                all_locations += data["data"]

    for poi in all_locations:
        store_url = "<MISSING>"
        if "null" not in poi["url"]:
            store_url = "https://www.jared.com" + poi["url"]
        location_name = poi["displayName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["line1"]
        if poi["line2"]:
            street_address += ", " + poi["line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["town"]
        city = city if city else "<MISSING>"
        state = poi["regionIsoCodeShort"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["name"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["openings"].items():
            hours_of_operation.append(f"{day} {hours}")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
