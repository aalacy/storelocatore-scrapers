import re
import csv
import demjson
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

    DOMAIN = "larryssubs.com"
    start_url = "https://larryssubs.com/find"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = (
        dom.xpath('//script[contains(text(), "var settings = ")]/text()')[0]
        .replace("\n", "")
        .replace("\t", "")
    )
    data = re.findall("settings =(.+?);var", data)[0]
    data = demjson.decode(data)

    all_locations = data["pins"]["pins"]
    for poi in all_locations:
        store_url = start_url
        location_type = "<MISSING>"
        location_name = poi["title"]
        street_address = "<MISSING>"
        city = poi["city"]
        state = "<MISSING>"
        zip_code = poi["zip"]
        country_code = "<MISSING>"
        store_number = location_name.split("#")[-1]
        phone = "<MISSING>"
        latitude = str(poi["latlng"][0])
        longitude = str(poi["latlng"][-1])
        hoo_html = etree.HTML(poi["tooltipContent"])
        hours_of_operation = hoo_html.xpath("//text()")[-1].split("Open")[-1].strip()
        splitter = re.findall(r"(#\d+)", location_name)[0]
        hours_of_operation = " ".join(
            [e.strip() for e in hours_of_operation.split()]
        ).split(splitter)[-1]
        if "OPEN SEASONALLY" in hours_of_operation:
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
