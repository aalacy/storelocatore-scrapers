import re
import csv
import json
from lxml import etree

from sgselenium import SgFirefox
from sgscrape.sgpostal import parse_address_usa


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

    start_url = "https://urbanplates.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
    data = dom.xpath('//script[contains(text(), "gmpAllMapsInfo")]/text()')[0]
    all_locations = re.findall("gmpAllMapsInfo = (.+);", data)[0]
    all_locations = json.loads(all_locations)

    for poi in all_locations[0]["markers"]:
        location_name = poi["title"]
        store_url = f'https://urbanplates.com/locations/{location_name.lower().replace(" ", "-")}'
        location_name = location_name if location_name else "<MISSING>"
        addr = parse_address_usa(poi["address"])
        street_address = addr.street_address_1
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["coord_x"]
        longitude = poi["coord_y"]
        hours_of_operation = "<MISSING>"

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
