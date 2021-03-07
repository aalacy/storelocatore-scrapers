import csv
import json
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    DOMAIN = "mydbsupply.com"
    start_url = "https://www.mydbsupply.com/Locations"

    items = []

    session = SgRequests()

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@id="hiddenLocationData"]/text()')[0]
    all_locations = json.loads(all_locations)

    for poi in all_locations:
        store_url = "https://www.mydbsupply.com/Locations"
        location_name = poi["branchName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        store_number = poi["branchId"]
        phone = poi["phone"]
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = etree.HTML(poi["workHour"]).xpath("//text()")
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
