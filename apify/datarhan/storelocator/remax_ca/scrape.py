import csv
import json
from urllib.parse import urljoin

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
    # Your scraper here
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "remax.ca"
    start_url = "https://www.remax.ca/api/v1/office/search/?from=0&size=16&category=Residential&text={}"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], max_radius_miles=100
    )
    for code in all_codes:
        response = session.get(start_url.format(code.replace(" ", "+")))
        data = json.loads(response.text)
        all_locations += data["result"]["results"]

    for poi in all_locations:
        store_url = urljoin("https://www.remax.ca", poi["detailUrl"])
        location_name = poi["officeName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address1"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postalCode"]
        country_code = poi["country"]
        store_number = "<MISSING>"
        phone = poi.get("telephone")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = "<MISSING>"

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
        if store_url not in scraped_items:
            scraped_items.append(store_url)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
