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

    start_url = "https://www.pendry.com/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath(
        '//h2[contains(text(), "Hotels & Resorts")]/following-sibling::ul[1]//a/@href'
    )
    for store_url in all_locations:
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')
        if poi:
            poi = json.loads(poi[0])

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
        else:
            location_name = loc_dom.xpath('//meta[@property="og:site_name"]/@content')
            location_name = location_name[0] if location_name else "<MISSING>"
            raw_address = loc_dom.xpath(
                '//span[@class="page-footer__address page-footer__address--small"]/a/text()'
            )
            if not raw_address:
                continue
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += addr.street_address_2
            street_address = street_address if street_address else "<MISSING>"
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = loc_dom.xpath(
                '//span[@class="page-footer__address page-footer__address--small"]/text()'
            )
            phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
            location_type = "<MISSING>"
            geo = (
                loc_dom.xpath(
                    '//span[@class="page-footer__address page-footer__address--small"]/a/@href'
                )[0]
                .split("/@")[-1]
                .split(",")[:2]
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
