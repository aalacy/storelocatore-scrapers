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

    DOMAIN = "delfriscosgrille.com"
    start_url = "https://delfriscosgrille.com/location-search/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    data = dom.xpath('//script[contains(text(), "locations:")]/text()')[0]
    data = re.findall(r"locations:(.+)", data)[0]
    data = json.loads(data[:-1])

    for poi in data:
        store_url = urljoin(start_url, poi["url"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        raw_address = poi["address"].split(", ")
        if len(raw_address) == 4:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        street_address = raw_address[0]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone_number"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Hours & Location")]/following-sibling::p[2]//text()'
        )
        hoo = [elem.strip() for elem in hoo]
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
