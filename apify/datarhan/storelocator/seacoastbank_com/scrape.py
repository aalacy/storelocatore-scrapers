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

    DOMAIN = "seacoastbank.com"
    start_url = "https://www.seacoastbank.com/locations/viera-suntree"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    data = (
        dom.xpath('//script[@id="marker-data"]/text()')[0]
        .split("markers =")[-1]
        .strip()[:-1]
    )
    data = re.sub(r"new google.maps.LatLng\((.+?)\)", r'"\1"', data.replace("\n", ""))
    all_locations = json.loads(data)

    for poi in all_locations:
        store_url = "<MISSING>"
        if poi["detailsURL"]:
            store_url = "https://www.seacoastbank.com" + poi["detailsURL"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["type"]
        geo = poi["coords"].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hoo = []
        if poi.get("hoursTableHTML"):
            hoo = etree.HTML(poi["hoursTableHTML"]).xpath("//td//text()")
            hoo = [e.strip() for e in hoo if e.strip()]
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
