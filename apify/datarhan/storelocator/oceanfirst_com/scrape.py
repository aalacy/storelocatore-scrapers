import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

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

    DOMAIN = "oceanfirst.com"
    start_url = "https://oceanfirst.com/locations/location-map/?loc=10001"

    response = session.get(start_url)
    all_locations = re.findall('a href="(.+?)">View Details', response.text)

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
        poi = json.loads(data)

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        if poi.get("address"):
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
        else:
            address_raw = loc_dom.xpath('//div[@class="branch-address f-h3"]/text()')
            address_raw = [elem.strip() for elem in address_raw if elem.strip()]
            if len(address_raw) == 3:
                address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
            street_address = address_raw[0]
            city = address_raw[1].split(", ")[0]
            state = address_raw[1].split(", ")[-1].split()[0]
            zip_code = address_raw[1].split(", ")[-1].split()[-1]
            country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi.get("telephone")
        if not phone:
            phone = loc_dom.xpath('//span[@class="phone"]/text()')
            if phone:
                phone = phone[0]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//div[@class="branch-hours"]/div[1]//text()'
        )[1:]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
