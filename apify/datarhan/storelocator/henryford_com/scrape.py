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
    scraped_items = []

    DOMAIN = "henryford.com"
    start_url = "https://www.henryford.com/locations"
    response = session.get(start_url)
    data = re.findall("locationsList = (.+?); var", response.text)[0]
    data = json.loads(data[1:-1])
    for e in data:
        for loc in e["Locations"]:
            store_url = urljoin(start_url, loc["Maps"])
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)

            location_name = loc["Name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = store_dom.xpath('//span[@id="address1"]/text()')[0]
            if store_dom.xpath('//span[@id="address2"]/text()'):
                street_address += (
                    ", " + store_dom.xpath('//span[@id="address2"]/text()')[0]
                )
            city = store_dom.xpath('//span[@id="city"]/text()')
            city = city[0].replace(",", "") if city else "<MISSING>"
            state = store_dom.xpath('//span[@id="state"]/text()')
            state = state[0].strip() if state else "<MISSING>"
            zip_code = store_dom.xpath('//span[@id="zip"]/text()')
            zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
            location_type = "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = store_dom.xpath('//div[@class="phones"]//a/text()')
            if not phone:
                phone = store_dom.xpath('//a[contains(@href, "tel")]/text()')
            if not phone:
                phone = store_dom.xpath(
                    '//*[strong[contains(text(), "Phone:")]]/text()'
                )
            if not phone:
                phone = store_dom.xpath('//p[contains(text(), "Phone:")]/text()')
            if not phone:
                phone = re.findall("first call (.+?) to schedule", store_response.text)
            phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<INACCESSIBLE>"

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

            check = f"{location_name} {street_address}"
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
