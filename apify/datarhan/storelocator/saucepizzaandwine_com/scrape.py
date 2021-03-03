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

    start_url = "https://www.saucepizzaandwine.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//a[contains(@href, "https://www.saucepizzaandwine.com/locations/")]/@href'
    )
    for store_url in list(set(all_locations)):
        if store_url == "https://www.saucepizzaandwine.com/locations/":
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "address")]/text()'
        )[0]
        poi = json.loads(poi)

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]
        store_number = "<MISSING>"
        phone = poi["telephone"]
        location_type = poi["@type"]
        latitude = re.findall("lat: (.+?),", loc_response.text)[0]
        longitude = re.findall("lng: (.+?)}", loc_response.text)[0]
        hoo = poi["openingHours"]
        hours_of_operation = hoo[0] if hoo else "<MISSING>"

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
