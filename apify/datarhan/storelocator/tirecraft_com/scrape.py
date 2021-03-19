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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://tirecraft.com/find-a-tirecraft/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "markers")]/text()')
    data = re.findall("markers = (\[.+?\]);", data[0])
    data = json.loads(data[0])

    for poi in data:
        store_url = poi["siteUrl"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["storeName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["storeAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["storeCity"]
        city = city if city else "<MISSING>"
        state = poi["storeRegion"]
        if not state:
            state = poi["storeProvince"]
        state = state if state else "<MISSING>"
        zip_code = poi["storePostal"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["storeID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["storePhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["storeLat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["storeLong"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["storeHours"]
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
