import re
import csv
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
    session = SgRequests()

    items = []

    DOMAIN = "slugandlettuce.co.uk"
    start_url = "https://www.slugandlettuce.co.uk/find-a-bar"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="sites-by-region"]//a/@href')
    all_locations = [elem for elem in all_locations if elem != "#"]

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="section-heading"]/text()')
        location_name = location_name[-1] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//ul[@class="menu vertical address"]/li/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = " ".join(address_raw[:-2])
        city = address_raw[-2].split("-")[0].strip()
        state = "<MISSING>"
        zip_code = address_raw[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall(r"lat: (.+?),", loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall(r"lng: (.+?) }", loc_response.text)
        longitude = longitude[-1].strip() if longitude else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Opening Times")]/following-sibling::div//text()'
        )
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
