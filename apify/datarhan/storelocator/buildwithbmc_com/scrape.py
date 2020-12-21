import csv
import json
from lxml import etree
from urllib.parse import urljoin

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
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "buildwithbmc.com"
    start_url = "https://www.buildwithbmc.com/bmc/store-finder"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//input[@class="region-iso"]/@value')
    for state in all_states:
        state_url = "https://www.buildwithbmc.com/bmc/store-finder?region=US-{}".format(
            state
        )
        response = session.get(state_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//div[@class="section2 search-result-item"]//a[contains(text(), "More Details")]/@href'
        )

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        store_response = session.get(store_url)
        dom = etree.HTML(store_response.text)
        store_data = dom.xpath('//div[@id="map_canvas"]/@data-stores')
        if not store_data:
            continue
        store_data = json.loads(store_data[0])

        address_raw = etree.HTML(store_data["name"])
        address_raw = address_raw.xpath("//text()")
        if len(address_raw) == 6:
            address_raw = [address_raw[0], ", ".join(address_raw[1:3])] + address_raw[
                3:
            ]
        location_name = address_raw[0]
        street_address = address_raw[1]
        city = address_raw[2]
        address_raw_2 = dom.xpath('//div[@class="detailSection section2"]/text()')
        address_raw_2 = [elem.strip() for elem in address_raw_2 if elem.strip()]
        state = address_raw_2[1].split(",")[-1].split()[0]
        zip_code = address_raw[3]
        country_code = address_raw[-1]
        store_number = dom.xpath('//input[@id="storename"]/@value')[0]
        phone = dom.xpath('//a[@class="phone-number phone-format bold-font"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = dom.xpath(
            '//h3[contains(text(), "Facility Type")]/following-sibling::div//label/text()'
        )
        location_type = ", ".join(location_type) if location_type else "<MISSING>"
        latitude = store_data["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = store_data["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = dom.xpath(
            '//div[@class="section1 puckup-hours section2"]/div//text()'
        )
        hours_of_operation = [
            elem.strip()
            for elem in hours_of_operation
            if elem.strip() and "/" not in elem
        ]
        hours_of_operation = [
            " ".join([e.strip() for e in elem.split()]) for elem in hours_of_operation
        ]
        hours_of_operation = " ".join(hours_of_operation)
        hours_of_operation = (
            hours_of_operation.replace(": - Monday", "Monday")
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
