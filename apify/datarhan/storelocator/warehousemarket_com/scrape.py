import re
import csv
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.warehousemarket.com/StoreLocator/State/?State=OK"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View")]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h1[contains(text(), "Store Information")]/following-sibling::h3/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//p[@class="Address"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = loc_response.url.split("=")[1].split("&")[0]
        phone = loc_dom.xpath('//p[@class="PhoneNumber"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall(r"initializeMap\((.+?)\);", loc_response.text)[0].split(",")
        latitude = geo[0][1:-1]
        longitude = geo[1][1:-1]
        hoo = loc_dom.xpath('//table[@id="hours_info-BS"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo[1:]).split(" Holiday")[0] if hoo else "<MISSING>"
        )

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
