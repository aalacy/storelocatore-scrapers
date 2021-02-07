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

    DOMAIN = "marlowstavern.com"
    start_url = "https://www.marlowstavern.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_poi = dom.xpath('//a[@class="directions"]/@href')
    for url in all_poi:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="location-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = (
            loc_dom.xpath('//a[@class="link-item location-address"]/text()')[0]
            .strip()
            .split("\n")
        )
        street_address = raw_address[0]
        city = raw_address[1][:-1]
        state = raw_address[2]
        zip_code = raw_address[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@class="link-item tel"]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//div[@class="hours-item simplewys"]/text()'
        )
        hours_of_operation = (
            " ".join(hours_of_operation).split("Patio")[0]
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
