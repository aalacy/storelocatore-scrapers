import re
import csv
from lxml import etree

from sgselenium import SgFirefox
from sgscrape.sgpostal import parse_address_usa


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

    start_url = "https://www.cheeziespizza.com/locations-results?gmw_post=locations&gmw_address%5B0%5D&gmw_distance=200&gmw_units=imperial&gmw_form=1&gmw_per_page=25&gmw_lat&gmw_lng&gmw_px=pt&action=gmw_post"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="wppl-single-result"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h2/a/@href")[0]
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        location_name = poi_html.xpath(".//h2/a/text()")[-1].strip()
        raw_address = poi_html.xpath('.//div[@class="wppl-address"]/text()')[0].strip()
        addr = parse_address_usa(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//div[@class="gmw-phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            poi_html.xpath('.//a[@title="Get Directions"]/@href')[0]
            .split("daddr=")[-1]
            .split("&")[0]
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]
        hoo = loc_dom.xpath('//div[@class="hours"]/text()')
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
