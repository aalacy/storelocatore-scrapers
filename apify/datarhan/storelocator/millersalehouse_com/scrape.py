import csv
import json
import urllib.parse
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
    session = SgRequests().requests_retry_session(retries=0)

    items = []
    scraped_items = []

    DOMAIN = "millersalehouse.com"
    start_url = "https://millersalehouse.com/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//ul[@class="state-locations"]//a/@href')

    for url in all_locations:
        store_url = urllib.parse.urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "postalCode")]/text()'
        )[0]
        data = json.loads(
            data.replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
            .replace('"R"', "R")
        )

        location_name = data["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["address"]["streetAddress"].replace("<br>", ", ")
        street_address = street_address if street_address else "<MISSING>"
        city = data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = data["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = data["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = loc_dom.xpath("//@data-location-id")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = data["telephone"]
        phone = phone if phone else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = data["@type"]
        location_type = location_type if location_type else "<MISSING>"
        hours_of_operation = data["openingHours"]
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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
