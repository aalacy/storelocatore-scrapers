import re
import csv
import json
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

    start_url = "https://factorymattresstexas.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace('www.', '')
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)
    data = dom.xpath('//script[contains(text(), "maplistScriptParamsKo")]//text()')[0]
    data = re.findall('maplistScriptParamsKo =(.+);', data)[0]
    data = json.loads(data)

    for poi in data['KOObject'][0]['locations']:
        store_url = poi['locationUrl']
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        location_name = poi['title']
        location_name = location_name if location_name else "<MISSING>"
        raw_address = etree.HTML(poi['address'])
        raw_address = raw_address.xpath('//text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(' '.join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ' ' + addr.street_address_2
        city = addr.city
        city = city if city else '<MISSING>'
        state = addr.state
        state = state if state else '<MISSING>'
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = addr.country
        country_code = country_code if country_code else '<MISSING>' 
        store_number = '<MISSING>'
        phone = etree.HTML(poi['description']).xpath('//div[@class="custom_phone"]/a/text()')
        phone = phone[0] if phone else '<MISSING>'
        location_type = '<MISSING>'
        latitude = poi['latitude']
        longitude = poi['longitude']
        hoo = loc_dom.xpath('//span[@itemprop="hours"]/text()')
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
