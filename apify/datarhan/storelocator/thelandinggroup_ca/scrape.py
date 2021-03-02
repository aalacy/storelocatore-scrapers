import re
import csv
from lxml import etree
from urllib.parse import urljoin

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

    DOMAIN = "thelandinggroup.ca"
    start_url = "https://thelandinggroup.ca/en/locations.html"

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[@class="we-ArticleTeaser-link"]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        raw_address = loc_dom.xpath('//p[i[@class="fa fa-map-marker"]]/text()')[
            0
        ].strip()

        location_name = loc_dom.xpath('//h1[@class="text-left"]/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//p[i[@class="fa fa-map-marker"]]/text()')[-1].strip()
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//script[contains(text(), "defaultLatitude")]/text()')[0]
        latitude = re.findall('defaultLatitude: "(.+?)",', geo)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall(r'defaultLongitude: "(.+?)",', geo)
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = hoo = loc_dom.xpath('//div[@id="hours_content"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
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
