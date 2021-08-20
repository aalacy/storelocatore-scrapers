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

    DOMAIN = "cruizers.net"
    start_url = "https://cruizers.net/wp-admin/admin-ajax.php?action=store_search&lat=40.75369&lng=-73.99916&max_results=100&search_radius=500"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://cruizers.net/locations/"
        location_name = poi["store"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = location_name.split("#")[-1]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = etree.HTML(poi["hours"]).xpath("//text()")
        hoo = [elem.strip() for elem in hoo if elem.strip()]
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
