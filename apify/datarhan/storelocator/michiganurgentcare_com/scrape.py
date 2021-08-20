import re
import csv
from lxml import etree

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

    start_url = "https://nextcare.com/brand/michigan-urgent-care/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="search-box-left"]/h3/a/@href')
    for store_url in all_locations:
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        location_name = loc_dom.xpath(
            '//h1[@class="elementor-heading-title elementor-size-default"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//li[@class="address-list"]/strong/text()')[0]
        addr = parse_address_intl(raw_address)
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
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//li[@class="tel-list"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        data = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[1]
        latitude = re.findall('latitude":(.+?),"', data)[0]
        longitude = re.findall('longitude":(.+?),"', data)[0]
        hoo = loc_dom.xpath('//ul[@class="day-list"]//text()')
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
