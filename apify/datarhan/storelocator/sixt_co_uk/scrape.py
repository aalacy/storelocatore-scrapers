import re
import csv
import json
import yaml
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

    DOMAIN = "sixt.co.uk"
    start_url = "https://www.sixt.co.uk/car-hire/united-kingdom/"

    all_locations = []
    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

        all_cities = dom.xpath('//div[@class="swiper-wrapper"]/a/@href')
        for url in all_cities:
            driver.get(urljoin(start_url, url))
            dom = etree.HTML(driver.page_source)
            data = dom.xpath('//script[contains(text(), "googleMarkers")]/text()')[0]
            data = re.findall("googleMarkers =(.+);", data)[0]
            data = yaml.load(data.replace("' + '", ""))
            for elem in data:
                all_locations.append(elem["locationLink"])

    for url in all_locations:
        store_url = urljoin(start_url, url)
        with SgChrome() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        poi = loc_dom.xpath('//script[contains(text(), "mainEntityOfPage")]/text()')[0]
        poi = json.loads(poi)

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressRegion"]
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        hoo = poi["openingHours"]
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
