import re
import csv
from lxml import etree
from time import sleep

from sgselenium import SgFirefox
from sgscrape.sgpostal import parse_address_intl


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

    start_url = "https://www.lelabofragrances.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        driver.find_element_by_xpath('//button[@data-category="Landing Page"]').click()
        sleep(3)
        driver.find_element_by_xpath(
            '//button[@class="optanon-allow-all accept-cookies-button"]'
        ).click()
        sleep(3)
        driver.find_element_by_xpath('//a[@data-label="Store Locator"]').click()
        sleep(3)
        driver.find_element_by_xpath(
            '//a[contains(text(), "View all locations")]'
        ).click()
        sleep(3)
        driver.find_element_by_xpath('//a[@data-country="US"]').click()
        sleep(3)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//ul[contains(@class, "list-locations")]/li')
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//a/h4/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="store-address"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["United Kingdom", "United States", "Canada"]:
            continue
        store_number = poi_html.xpath('.//div[@class="store-name"]/a/@id')[0]
        phone = poi_html.xpath('.//div[@class="store-number"]/a/text()')
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="store-hours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        if hoo:
            if "Temporarily closed" in hoo[0]:
                location_type = "temporarily closed"
        hours_of_operation = (
            " ".join(hoo).split("Available")[-1] if hoo else "<MISSING>"
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
