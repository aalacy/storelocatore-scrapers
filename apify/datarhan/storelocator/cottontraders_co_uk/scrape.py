import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "cottontraders.com"
    start_url = "https://www.cottontraders.com/stores/"

    response = session.get(start_url, verify=False)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//select[@data-cmp="inputSelect"]//@data-url')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "addressLocality")]/text()'
        )[0]
        poi = json.loads(poi)

        location_name = poi["name"]
        addr = " ".join(
            loc_dom.xpath(
                '//div[@class="b-store-locator_full-details_store_address"]/div/text()'
            )
        )
        addr = parse_address_intl(addr)
        street_address = poi["address"]["streetAddress"]
        city = addr.city
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["addressCountry"]
        store_number = store_url.split("=")[-1]
        phone = poi["telephone"]
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        hours_of_operation = poi["openingHours"]
        if not hours_of_operation:
            hours_of_operation = "Temporarily closed"

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
