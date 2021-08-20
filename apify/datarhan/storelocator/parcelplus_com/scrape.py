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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "parcelplus.com"
    start_url = "https://www.parcelplus.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//span[@class="weblink"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath("//h1/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//div[@class="street-block"]/div/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@class="locality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@class="state"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@class="postal-code"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@class="phonetel3"]/text()')
        phone = phone[0] if phone and phone[0].strip() else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall('lat":(.+?),', loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall('lon":(.+?)}', loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[contains(@class, "store-hours")]//text()')
        hoo = [elem.replace("Store Hours ", "").strip() for elem in hoo if elem.strip()]
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
