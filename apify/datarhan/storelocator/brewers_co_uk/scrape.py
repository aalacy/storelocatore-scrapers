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

    DOMAIN = "brewers.co.uk"
    start_url = "https://www.brewers.co.uk/stores/stores"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(@href, "/stores/")]/@href')
    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath("//@ng-init")[0]
        data = re.findall(r"initSingle\((.+)\)", data)[0]
        poi = json.loads(data)[0]

        location_name = loc_dom.xpath('//h1[@class="inline h2"]/text()')
        location_name = (
            " ".join(location_name[0].split()).strip() if location_name else "<MISSING>"
        )
        street_address = poi["address1"]
        street_address = street_address if street_address else "<MISSING>"
        if poi["address2"]:
            street_address += " " + poi["address2"]
        street_address = " ".join(
            [elem.strip() for elem in street_address.split() if elem.strip()]
        ).replace("  ", " ")
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["county"]
        state = state if state else "<MISSING>"
        zip_code = poi["postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//dl[@class="inline"]//text()')
        hoo = [" ".join(elem.split()) for elem in hoo if elem.strip()]
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
