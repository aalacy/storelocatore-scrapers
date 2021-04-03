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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://storerocket.global.ssl.fastly.net/api/user/6wpZjxZpAn/locations?radius=20&units=miles"
    domain = "tanrepublic.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = json.loads(response.text)

    all_locations = data["results"]["locations"]
    for poi in all_locations:
        store_url = urljoin("https://www.tanrepublic.com/", poi["slug"])
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"].split(",")[0]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["marker_id"]
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = []
        for day, hours in poi["hours"].items():
            if not hours:
                hours = "closed"
            hoo.append(f"{day} {hours}")
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
