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

    DOMAIN = "saxbyscoffee.com"
    start_url = "https://www.saxbyscoffee.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@type="application/ld+json"]/text()')[0]
    data = json.loads(data)

    for poi in data["subOrganization"]:
        store_url = poi["url"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        latitude = loc_dom.xpath("//@data-gmaps-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-gmaps-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//p[contains(text(), "Operating Hours:")]/following-sibling::p/text()'
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
