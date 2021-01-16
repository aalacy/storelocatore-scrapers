import re
import csv
import json
from urllib.parse import urljoin
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox


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

    DOMAIN = "kekes.com"
    start_url = "https://www.kekes.com/all-locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="sqs-block-content"]/p/a/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)
        poi = loc_dom.xpath("//div/@data-block-json")
        if not poi:
            continue
        poi = json.loads(poi[0])
        if not poi["location"]["addressLine2"]:
            continue

        location_name = loc_dom.xpath('//div[@class="sqs-block-content"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi["location"]["addressLine1"]
        street_address = street_address if street_address else "<MISSING>"
        city = "<MISSING>"
        if len(poi["location"]["addressLine2"].split(", ")) == 3:
            city = poi["location"]["addressLine2"].split(", ")[0]
        state = poi["location"]["addressLine2"].split(", ")[-2]
        zip_code = poi["location"]["addressLine2"].split(", ")[-1]
        country_code = poi["location"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["location"]["mapZoom"]
        store_number = store_number if store_number else "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["mapLat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["location"]["mapLng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//p[contains(text(), "open daily")]/text()')[0]
        hours_of_operation = re.findall(r"locations are (.+)\(", hoo)[0]

        if city.split(",")[0].isdigit():
            city = "<MISSING>"
        if state.split(",")[0].isdigit():
            state = "<MISSING>"
        if len(zip_code.split()) == 2:
            city = state
            state = zip_code.split()[0]
            zip_code = zip_code.split()[-1]
        if street_address == "<MISSING>":
            state = "<MISSING>"
            zip_code = "<MISSING>"

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
