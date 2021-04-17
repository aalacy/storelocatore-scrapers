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

    start_url = "https://www.filson.com/store-locator"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath("//div/@data-locations")[0]
    data = json.loads(data)

    for poi in data:
        location_name = poi["location_name"]
        store_url = dom.xpath(
            '//a[*[contains(text(), "{}")]]/@href'.format(location_name)
        )
        if not store_url:
            store_url = dom.xpath(
                '//a[*[contains(text(), "{}")]]/@href'.format(location_name.split()[0])
            )
        store_url = urljoin(start_url, store_url[0]) if store_url else start_url
        street_address = poi["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zipcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["United States", "Canada"]:
            continue
        store_number = poi["record_id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["position"]["latitude"]
        longitude = poi["position"]["longitude"]
        hours_of_operation = "<MISSING>"

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
