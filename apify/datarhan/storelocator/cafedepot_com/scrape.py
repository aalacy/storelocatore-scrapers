import re
import csv
from time import sleep
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

    start_url = "https://cafedepot.com/find-a-cafe-2/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(5)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath(
        '//span[@class="store-locator__store-list"]//div[contains(@id, "store")]'
    )
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(
            './/div[contains(@class, "store-location")]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = "<MISSING>"
        city = (
            poi_html.xpath('.//div[contains(@class, "store-address")]/text()')[0]
            .split("Canada")[0]
            .strip()[:-1]
            .split()[:-1]
        )
        city = " ".join(city)
        state = (
            poi_html.xpath('.//div[contains(@class, "store-address")]/text()')[0]
            .split("Canada")[0]
            .strip()[:-1]
            .split()[-1]
        )
        zip_code = "<MISSING>"
        country_code = "Canada"
        store_number = location_name.split("-")[0].split()[0]
        phone = (
            poi_html.xpath('.//div[contains(@class, "store-address")]/text()')[0]
            .split("Canada")[-1]
            .strip()
        )
        location_type = "<MISSING>"
        geo = (
            poi_html.xpath('.//a[contains(@href, "maps")]/@href')[0]
            .split("=(")[-1][:-1]
            .split(", ")
        )
        latitude = geo[0]
        longitude = geo[1]
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
