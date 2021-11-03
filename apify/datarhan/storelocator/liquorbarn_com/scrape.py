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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "liquorbarn.com"
    start_url = "https://liquorbarn.com/wp-admin/admin-ajax.php?action=store_search&lat=38.252665&lng=-85.758456&max_results=25&search_radius=50&autoload=1"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["permalink"]
        location_type = "<MISSING>"
        hoo = etree.HTML(poi["hours"])
        hoo = hoo.xpath("//text()")
        hours_of_operation = " ".join(hoo) if (hoo) else "<MISSING>"
        location_name = poi["store"]
        street_address = poi["address"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        latitude = poi["lat"]
        longitude = poi["lng"]

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
