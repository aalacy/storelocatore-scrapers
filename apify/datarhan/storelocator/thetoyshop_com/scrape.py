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
    items = []

    session = SgRequests()

    DOMAIN = "thetoyshop.com"
    start_url = "https://www.thetoyshop.com/store-finder"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath("//li/@data-url")
    all_locations = []
    for url in all_urls:
        response = session.get(urljoin(start_url, url))
        data = json.loads(response.text)
        all_locations += data["data"]

    for poi in all_locations:
        store_url = "https://www.thetoyshop.com" + poi["url"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["line1"]
        if poi["line2"]:
            street_address += " " + poi["line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["town"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for d, h in poi["openings"].items():
            hoo.append(f"{d} {h}")
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
