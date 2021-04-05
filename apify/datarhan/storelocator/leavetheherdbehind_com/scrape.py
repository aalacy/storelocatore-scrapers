import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgChrome
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
    session = SgRequests()

    items = []

    DOMAIN = "leavetheherdbehind.com"
    start_url = "https://leavetheherdbehind.com/blogs/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="single-location__image"]/@href')
    for store_url in all_locations:
        store_url = urljoin(start_url, store_url)
        with SgChrome() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

        location_name = loc_dom.xpath(
            '//h1[@class="hero__title title-lg location-title-label"]/span/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath("//address/p/text()")[0]
        addr = parse_address_intl(address_raw)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_1
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "UK"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        geo_data = loc_dom.xpath('//script[contains(text(), "center:")]/text()')[0]
        geo = re.findall(r"center: \[(.+?)\],", geo_data)[0].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hours_of_operation = loc_dom.xpath(
            '//h2[contains(text(), "Opening Hours")]/following-sibling::div/span/text()'
        )
        if not hours_of_operation:
            hours_of_operation = loc_dom.xpath(
                '//h2[contains(text(), "opening hours")]/following-sibling::div/span/text()'
            )
        if not hours_of_operation:
            hours_of_operation = loc_dom.xpath(
                '//h2[contains(text(), "OPENING HOURS")]/following-sibling::div/span/text()'
            )
        if not hours_of_operation:
            hours_of_operation = loc_dom.xpath(
                '//h2[contains(text(), "opening hours")]/following-sibling::div//p//text()'
            )
            hours_of_operation = [
                elem.strip()
                for elem in hours_of_operation
                if elem.strip() and "am" in elem
            ]
        if not hours_of_operation:
            hours_of_operation = []
            id_data = loc_dom.xpath('//script[contains(text(), "var id")]/text()')[0]
            store_id = re.findall(r"var id=\'(\d+)\'", id_data)[0]
            hoo_response = session.get(
                f"https://backend.cheerfy.com/shop-service/timetable/?scope_locations={store_id}"
            )
            hoo = json.loads(hoo_response.text)
            for elem in hoo["timetable"]:
                day = elem["day"]
                opens = elem["intervals"][0]["open_at"]
                closes = elem["intervals"][0]["close_at"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        hours_of_operation = (
            hours_of_operation
            if hours_of_operation and hours_of_operation.strip()
            else "<MISSING>"
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
