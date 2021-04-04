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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "guitarcenter.com"
    start_url = "https://www.gw-supermarket.com/our-store/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = re.findall(r"maps\((.+)\).data", response.text)[0]
    data = json.loads(data)

    for poi in data["places"]:
        store_url = "<MISSING>"
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"].split(",")[0]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"].split(",")[1].strip()
        city = city if city else "<MISSING>"
        state = poi["location"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["location"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = dom.xpath(
            '//h3[contains(text(), "{}")]//following-sibling::div[1]//p[contains(text(), "Tel")]/text()'.format(
                poi["title"]
            )
        )
        if not phone:
            phone = dom.xpath(
                '//p[a[contains(text(), "{}")]]/following-sibling::p[contains(text(), "Tel")]/text()'.format(
                    zip_code
                )
            )
        phone = phone[0].split(":")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["location"]["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = dom.xpath(
            '//h3[contains(text(), "{}")]//following-sibling::div[1]//p[contains(text(), "Open Hours")]/text()'.format(
                poi["title"]
            )
        )
        if not hours_of_operation:
            hours_of_operation = dom.xpath(
                '//h3[contains(text(), "{}")]//following-sibling::div[1]//p[contains(text(), "营业时间")]/text()'.format(
                    poi["title"]
                )
            )
        if not hours_of_operation:
            hours_of_operation = dom.xpath(
                '//p[a[contains(text(), "{}")]]/following-sibling::p[contains(text(), "Open Hours")]/text()'.format(
                    zip_code
                )
            )
        hours_of_operation = (
            hours_of_operation[0]
            .replace("Open Hours：", "")
            .replace("营业时间：", "")
            .replace("营业时间:", "")
            if hours_of_operation
            else "<MISSING>"
        )

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
