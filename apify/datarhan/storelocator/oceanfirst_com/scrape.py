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

    DOMAIN = "oceanfirst.com"
    start_url = "https://oceanfirst.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//p[@class="actions"]/a[1]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="branch-address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        location_type = "<MISSING>"
        if "Temporarily Closed" in raw_address[0]:
            raw_address = raw_address[1:]
            location_type = "Temporarily Closed"
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@class="phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        geo = re.findall(r"LatLng\((.+)\)", loc_response.text)[0].split(", ")
        latitude = geo[0]
        longitude = geo[1]
        hoo = loc_dom.xpath('//div[@class="branch_hours_days clearfix"]//text()')
        hoo = " ".join(hoo).split("January")[0].strip() if hoo else "<MISSING>"
        hours_of_operation = hoo.strip() if hoo and hoo.strip() else "<MISSING>"

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
