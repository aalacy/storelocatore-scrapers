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
    session = SgRequests()

    items = []

    DOMAIN = "flyersenergy.com"
    start_url = "https://www.flyersenergy.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath(
        '//script[contains(text(), "wpgmaps_localize_marker_data")]/text()'
    )[0]
    data = re.findall("wpgmaps_localize_marker_data = (.+?);", data.replace("\n", ""))[
        0
    ]
    data = json.loads(data)

    for poi in data["1"].values():
        store_url = "https://www.flyersenergy.com/locations/"
        location_name = poi["title"]
        street_address = poi["address"].split(", ")[0]
        city = poi["address"].split(", ")[1]
        state = poi["address"].split(", ")[-1].split()[0]
        zip_code = poi["address"].split(", ")[-1].split()[-1]
        latitude = poi["lat"]
        longitude = poi["lng"]
        country_code = "<MISSING>"
        store_number = re.findall(r"(\d+) -", poi["title"])[0]
        phone = "<MISSING>"
        location_type = "<MISSING>"
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
