import re
import csv
import json
from w3lib.url import add_or_replace_parameter

from sgselenium import SgFirefox


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
    items = []
    scraped_items = []

    DOMAIN = "sportsmans.com"
    start_url = "https://www.sportsmans.com/store-locator?q=08854&page=0"

    all_locations = []
    with SgFirefox() as driver:
        driver.get("https://www.sportsmans.com/store-locator")
        driver.get(start_url)
        print(driver.page_source)
        data = re.findall("<body>(.+)</body>", driver.page_source.replace("\n", ""))[0]
        data = json.loads(data)
        all_locations += data["data"]
        total_pages = data["total"] // 10 + 1
        for page in range(1, total_pages):
            driver.get(add_or_replace_parameter(start_url, "page", str(page)))
            data = re.findall(
                "<body>(.+)</body>", driver.page_source.replace("\n", "")
            )[0]
            data = json.loads(data)
            all_locations += data["data"]

    for poi in all_locations:
        store_url = poi["url"]
        location_name = "{} {} {}".format(
            poi["warehouseNameStart"], poi["warehouseNameEnd"], poi["name"]
        )
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["town"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["name"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
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
