import re
import csv
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgpostal import USA_Best_Parser, parse_address


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

    DOMAIN = "biscuitscafe.com"
    start_urls = [
        "https://www.biscuitscafe.com/arizona/",
        "https://www.biscuitscafe.com/oregon/",
        "https://www.biscuitscafe.com/washington/",
    ]

    all_locations = []
    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@data-vc-content=".vc_tta-panel-body"]')

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//span[@class="vc_tta-title-text"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="wpb_wrapper"]/*[1]/text()')
        if not street_address:
            street_address = poi_html.xpath('.//div[@class="wpb_wrapper"]/p[2]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="wpb_wrapper"]//text()')
        if not raw_address:
            raw_address = poi_html.xpath('.//div[@class="wpb_wrapper"]/*[2]/text()')

        raw = " ".join([elem.strip() for elem in raw_address[:4] if elem.strip()])
        parsed_addr = parse_address(raw, USA_Best_Parser())
        city = parsed_addr.city
        state = parsed_addr.state
        zip_code = parsed_addr.postcode
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('//*[strong[contains(text(), "Phone:")]]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = poi_html.xpath(".//iframe/@src")[0]
        latitude = re.findall(r"\d\d.\d\d\d\d\d\d\d\d\d\d\d\d", geo)
        latitude = latitude[-1] if latitude else ""
        if not latitude:
            latitude = re.findall(r"\d\d.\d\d\d\d\d\d", geo)[-1]
        longitude = re.findall(r"-\d\d\d.\d\d\d\d\d\d\d\d\d\d\d\d", geo)
        longitude = longitude[0] if longitude else ""
        if not longitude:
            longitude = re.findall(r"-\d\d\d.\d\d\d\d\d\d", geo)
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
