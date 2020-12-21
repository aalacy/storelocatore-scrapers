import re
import csv
import json
from lxml import etree
from w3lib.html import remove_tags

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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "specsonline.com"
    start_url = "https://specsonline.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@class="instore-store "]//a[contains(text(), "location detail")]/@href'
    )
    all_locations += dom.xpath(
        '//div[@class="instore-store hidden-stores"]//a[contains(text(), "location detail")]/@href'
    )

    data = dom.xpath('//script[@id="maplistko-js-extra"]/text()')[0]
    data = re.findall("ParamsKo =(.+);", data)[0]
    data = json.loads(data)

    for poi in data["KOObject"][0]["locations"]:
        store_url = poi["locationUrl"]
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = remove_tags(poi["address"]).split("\n")[0]
        city = remove_tags(poi["address"]).split("\n")[1].split(",")[0]
        state = remove_tags(poi["address"]).split("\n")[1].split(",")[-1].split()[0]
        zip_code = remove_tags(poi["address"]).split("\n")[1].split(",")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = ""
        if poi.get("simpledescription"):
            phone = remove_tags(poi["simpledescription"]).split()[0]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = "<MISSING>"

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
