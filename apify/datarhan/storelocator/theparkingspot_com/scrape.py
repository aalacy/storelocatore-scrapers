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

    DOMAIN = "theparkingspot.com"
    start_url = "https://www.theparkingspot.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//section[@class="airport-locations-block-list"]//a/@href')
    all_locations = []
    for url in all_urls:
        if len(url.split("/")) == 5:
            all_locations.append(url)
            continue
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//div[@class="airport-facilities__location"]/div/a/@href'
        )

    for store_url in list(set(all_locations)):
        store_url = urljoin(start_url, store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[-1]
        poi = json.loads(poi)

        location_name = poi["@graph"][0]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["@graph"][0]["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["@graph"][0]["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["@graph"][0]["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["@graph"][0]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["@graph"][0]["address"]["addressCountry"]
        store_number = "<MISSING>"
        phone = poi["@graph"][0]["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@graph"][0]["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["@graph"][0]["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["@graph"][0]["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["@graph"][0]["openingHours"]

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
