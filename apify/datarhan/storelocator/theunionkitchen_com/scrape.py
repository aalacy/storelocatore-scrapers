import re
import csv
import json
from lxml import etree

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

    start_url = "https://www.theunionkitchen.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//script[contains(text(), "Restaurant")]/text()')[1:]
    for poi in all_locations:
        poi = json.loads(poi)
        store_url = start_url
        location_name = poi["address"]["addressLocality"]
        street_address = poi["address"]["streetAddress"].replace("\n", " ")
        city = poi["address"]["addressLocality"]
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["address"]["telephone"]
        location_type = poi["@type"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi["openingHours"]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
