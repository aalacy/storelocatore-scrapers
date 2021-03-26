import re
import csv
import json
from lxml import etree
from time import sleep
from urllib.parse import urljoin

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

    start_url = "https://www.redlion.com/locations"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    all_locations = []
    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)
        all_states = dom.xpath('//ul[contains(@class, "locations__List")]//a/@href')
        for url in all_states:
            state_url = urljoin(start_url, url)
            driver.get(state_url)
            sleep(4)
            state_dom = etree.HTML(driver.page_source)
            all_cities = state_dom.xpath(
                '//ul[contains(@class, "region__List")]//a/@href'
            )
            for url in all_cities:
                city_url = urljoin(start_url, url)
                driver.get(city_url)
                sleep(4)
                city_dom = etree.HTML(driver.page_source)
                all_locations += city_dom.xpath('//h4[@itemprop="name"]/a/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        with SgFirefox() as driver:
            driver.get(store_url)
            sleep(4)
            loc_dom = etree.HTML(driver.page_source)
            poi = loc_dom.xpath('//script[@data-react-helmet="true"]/text()')
            if not poi:
                sleep(10)
                loc_dom = etree.HTML(driver.page_source)
                poi = loc_dom.xpath('//script[@data-react-helmet="true"]/text()')

        poi = poi[-1]
        if "streetAddress" not in poi:
            continue
        poi = json.loads(poi)

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
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
        store_number = "<MISSING>"
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
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
