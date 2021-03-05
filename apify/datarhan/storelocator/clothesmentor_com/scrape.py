import re
import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgselenium import SgChrome


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

    DOMAIN = "clothesmentor.com"
    start_url = "https://clothesmentor.com/apps/store-locator/all"
    with SgChrome() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath(
        '//form[@id="frm-storelocator-search"]//div[@datamarker]//a[@class="linkdetailstore"]/@href'
    )
    for url in all_locations:
        store_url = urljoin(start_url, url)
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//div[@class="section-header"]/h1/span/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        address_raw = store_dom.xpath(
            '//div[@class="content-store-info"]/div[@class="entry-info"]/div/text()'
        )
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        address_raw = address_raw[0].split(",")
        if len(address_raw) == 4:
            address_raw = address_raw[:3] + ["<MISSING>"] + address_raw[3:]
        if len(address_raw) == 6:
            address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
        street_address = address_raw[0]
        city = address_raw[1].strip()
        state = address_raw[2].strip()
        zip_code = address_raw[3].strip()
        country_code = address_raw[4].strip()
        store_number = "<MISSING>"
        phone = store_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall("lat:(.+),lng", store_response.text)[0]
        longitude = re.findall("lng:(.+) };", store_response.text)[0]
        hours_of_operation = store_dom.xpath(
            '//table[@class="work-time table"]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
