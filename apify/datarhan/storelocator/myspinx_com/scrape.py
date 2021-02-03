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

    DOMAIN = "myspinx.com"
    start_url = "https://www.myspinx.com/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//td[@class="info-cell"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = "Store " + loc_dom.xpath('//span[@class="number"]/text()')[0]
        raw_address = loc_dom.xpath('//p[@class="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address]
        street_address = raw_address[0]
        street_address = street_address if street_address else "<MISSING>"
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[1]
        zip_code = raw_address[1].split(", ")[2]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = loc_dom.xpath('//span[@class="number"]/text()')[0][1:]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[-1].strip()
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//script[contains(text(), "LOCATIONS = ")]/text()')[0]
        geo = json.loads(re.findall(" = (.+?);", geo)[0])
        latitude = geo[0]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[0]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
