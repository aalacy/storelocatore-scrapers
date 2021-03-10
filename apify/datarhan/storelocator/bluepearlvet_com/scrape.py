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

    DOMAIN = "bluepearlvet.com"
    start_url = "https://bluepearlvet.com/find-a-hospital/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@class="location-map__name"]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
        data = json.loads(data)

        location_name = data["name"].replace("<br>", " ")
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = data["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = data["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = data["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        location_type = data["@type"]
        location_type = location_type if location_type else "<MISSING>"
        geo = (
            loc_dom.xpath('//div[@class="banner-location__content"]/a/@href')[0]
            .split("=")[-1]
            .split(",")
        )
        latitude = geo[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = geo[1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"
        phone = data["telephone"]
        phone = phone if phone else "<MISSING>"

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
