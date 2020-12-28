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
    session = SgRequests()

    items = []

    DOMAIN = "latan.com"
    start_url = "http://latan.com/our-locations/"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_states = dom.xpath('//div[@class="location-page"]//li/a/@href')
    for url in all_states:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[@class="btn location-btn"]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="header-details"]/h3/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath('//div[@class="header-details"]/p/text()')
        street_address = address_raw[0]
        city = location_name
        city = city if city else "<MISSING>"
        state = address_raw[1].split()[0]
        state = state if state else "<MISSING>"
        zip_code = address_raw[1].split()[-1]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        phone = address_raw[-1]
        phone = phone if phone else "<MISSING>"
        latitude = re.findall("latitude = '(.+)';", loc_response.text)[0]
        longitude = re.findall("longitude = '(.+)';", loc_response.text)[0]
        hours_of_operation = loc_dom.xpath('//div[@class="hours"]//li/p/text()')
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
