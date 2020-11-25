import re
import csv
from lxml import etree

from sgrequests import SgRequests


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

    DOMAIN = "familyvideo.com"

    start_url = "https://www.familyvideo.com/storelocator/"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_poi_html = dom.xpath('//div[@class="amlocator-stores-wrapper"]/div')
    for poi_html in all_poi_html:
        store_url = poi_html.xpath('.//a[@class="amlocator-link"]/@href')[0]
        location_name = poi_html.xpath('.//a[@class="amlocator-link"]/text()')[0]
        location_name = location_name if location_name else "<MISSING>"
        address_raw = poi_html.xpath(
            './/div[@class="amlocator-store-information"]/text()'
        )
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[-1].split(":")[-1]
        street_address = street_address if street_address else "<MISSING>"
        city = address_raw[0].split(":")[-1]
        city = city if city else "<MISSING>"
        state = address_raw[2].split(":")[-1]
        state = state if state else "<MISSING>"
        zip_code = address_raw[1].split(":")[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = ""
        country_code = country_code if country_code else "<MISSING>"
        store_number = ""
        store_number = store_number if store_number else "<MISSING>"

        poi_response = session.get(store_url)
        poi_dom = etree.HTML(poi_response.text)
        phone = poi_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        geo_data = poi_dom.xpath('//script[contains(text(), "lng:")]/text()')[
            0
        ].replace("\n", "")
        latitude = re.findall("lat: (.+?),", geo_data)[0]
        longitude = re.findall("lng: (.+?),", geo_data)[0]
        hours_of_operation = []
        hours_html = poi_dom.xpath('//div[@class="amlocator-schedule-table"]/div')
        for elem in hours_html:
            day = elem.xpath(".//text()")[1].strip()
            hours = elem.xpath(".//text()")[3].strip()
            hours_of_operation.append("{} {}".format(day, hours))
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
