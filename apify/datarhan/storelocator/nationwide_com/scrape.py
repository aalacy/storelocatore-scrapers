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

    DOMAIN = "nationwide.com"

    start_url = "https://agency.nationwide.com/search-api?agencyName=&q={}"
    headers = {
        "accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=30
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=headers)
        data = json.loads(response.text)
        all_locations += data["locations"]

    for poi in all_locations:
        store_url = urljoin(start_url, poi["url"])
        location_name = poi["loc"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["loc"]["address1"]
        if poi["loc"]["address2"]:
            street_address += " " + poi["loc"]["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["loc"]["city"]
        city = city if city else "<MISSING>"
        state = poi["loc"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["loc"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["loc"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["loc"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["loc"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["loc"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["loc"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
