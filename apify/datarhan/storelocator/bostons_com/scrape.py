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

    DOMAIN = "bostons.com"
    start_url = "https://www.bostons.com/locations/index.html?location=all"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_stores = dom.xpath('//a[@itemprop="url"]/@href')
    for url in all_stores:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//script[contains(text(), "var data =")]/text()')[0]
        data = re.findall("var data = (.+?) var", data.replace("\n", ""))[0]
        data = json.loads(data)

        location_name = data["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = data["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = data["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = data["@type"]
        latitude = data["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = data["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="location__meta-hours-list"]/dl//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip]
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
