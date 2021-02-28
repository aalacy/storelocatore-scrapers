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

    DOMAIN = "remax.co.uk"
    start_url = "https://www.remax.co.uk/branch/offices"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(),"Go to Office Website")]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath(
            '//h4[contains(text(), "Office Address")]/following-sibling::p[@class="branch-text"]/text()'
        )
        raw_address = [e.strip() for e in raw_address if e.strip()]
        location_name = loc_dom.xpath('//h1[@class="white branch-name-wrap"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[2]
        zip_code = raw_address[-1]
        country_code = "UK"
        store_number = loc_response.url.split("bid=")[-1].split(",")[0]
        phone = loc_dom.xpath('//div[@class="branch-telephone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall(r"LatLng\((.+)\);", loc_response.text)[0].split(",")
        latitude = geo[0].strip() if geo[0].strip() else "<MISSING>"
        longitude = geo[1].strip() if geo[1].strip() else "<MISSING>"
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Opening hours")]/following-sibling::p[@class="branch-text"]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
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
