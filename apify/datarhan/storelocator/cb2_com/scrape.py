import csv
import json
from lxml import etree
from time import sleep

from sgselenium.sgselenium import webdriver

option = webdriver.ChromeOptions()
option.add_argument("--disable-blink-features=AutomationControlled")


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

    DOMAIN = "cb2.com"
    start_url = "https://www.cb2.com/stores/"

    with webdriver.Chrome(options=option) as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//script[@type="application/ld+json"]/text()')
    for elem in all_locations:
        poi = json.loads(elem)
        if not poi.get("image"):
            continue
        location_name = poi["name"]
        store_number = poi["image"].split("-")[-2]
        store_url = "https://www.cb2.com/stores/{}/str{}".format(
            location_name.replace(" ", "-").lower(), store_number
        )
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["openingHours"]
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
