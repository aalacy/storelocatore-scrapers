import re
import csv
import json
from lxml import etree

from sgselenium import SgFirefox


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

    start_url = "https://www.theunionkitchen.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//script[contains(text(), "Restaurant")]/text()')[1:]
    for poi in all_locations:
        poi = json.loads(poi)
        store_url = start_url
        street_address = poi["address"]["streetAddress"].replace("\n", " ")
        poi_html = dom.xpath(
            '//section[p[a[span[contains(text(), "{}")]]]]'.format(
                " ".join(street_address.split()[:2])
            )
        )[0]
        if street_address.endswith(","):
            street_address = street_address[:-1]
        location_name = poi_html.xpath(".//h4/text()")[0]
        city = poi["address"]["addressLocality"]
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["address"]["telephone"]
        location_type = poi["@type"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="hours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
