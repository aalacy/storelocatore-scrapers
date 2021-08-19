import re
import csv
from lxml import etree

from sgrequests import SgRequests
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

    DOMAIN = "booths.co.uk"
    start_url = "https://www.booths.co.uk/stores/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_stores = dom.xpath(
        '//h2[contains(text(), "Full Store List")]/following-sibling::ol/li/a/@href'
    )
    for store_url in all_stores:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = " ".join(loc_dom.xpath("//address/text()"))
        addrr = parse_address_intl(raw_address)

        location_name = loc_dom.xpath('//h1[@class="divider secundus"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = addrr.street_address_1
        street_address = street_address if street_address else "<MISSING>"
        city = addrr.city
        city = city if city else "<MISSING>"
        state = addrr.state
        state = state if state else "<MISSING>"
        zip_code = addrr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "UK"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//li[@class="phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall(r"LatLng\((.+?)\);", loc_response.text)[0].split(", ")
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//h4[contains(text(), "Store Opening Times")]/following-sibling::dl//text()'
        )
        hours_of_operation = [elem.strip() for elem in hours_of_operation if elem.strip]
        hours_of_operation = (
            " ".join(hours_of_operation).split("*")[0]
            if hours_of_operation
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
