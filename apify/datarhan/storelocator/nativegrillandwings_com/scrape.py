import re
import csv
import json
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

    DOMAIN = "nativegrillandwings.com"
    start_url = "https://nativegrillandwings.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//h3/a[contains(@href, "/location/")]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "wpslMap_0=")]/text()')[0]
        poi = re.findall("wpslMap_0=(.+?);", poi.replace("&#8211;", ""))[0]
        poi = json.loads(poi)

        location_name = poi["locations"][0]["store"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["locations"][0]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["locations"][0]["city"]
        city = city if city else "<MISSING>"
        state = poi["locations"][0]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["locations"][0]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["locations"][0]["country"]
        store_number = poi["locations"][0]["id"]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["locations"][0]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["locations"][0]["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//table[@class="wpsl-opening-hours"]//text()'
        )
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
