import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgselenium import SgChrome


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

    DOMAIN = "delfriscosgrille.com"
    start_url = "https://delfriscosgrille.com/location-search/"

    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    data = dom.xpath('//script[contains(text(), "ld_locations = ")]/text()')[0]
    data = re.findall("locations = (.+)", data)[0]
    data = json.loads(data)

    for poi in data:
        base_url = "https://delfriscosgrille.com"
        store_url = urljoin(base_url, poi["id"])
        with SgChrome() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

        location_name = poi["city_state"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["long"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Hours")]/following-sibling::p/text()'
        )
        hoo = [elem.strip() for elem in hoo]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
