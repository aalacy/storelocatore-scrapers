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

    DOMAIN = "akumin.com"
    start_url = "https://akumin.com/#centers"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[contains(@class, "location")]/a/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="center maintitle"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = loc_dom.xpath(
            '//strong[contains(text(), "Address:")]/following::text()'
        )[:2]
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        street_address = address_raw[0].replace(",", "")
        city = address_raw[1].split(",")[0]
        country_code = "<MISSING>"
        state = address_raw[1].split(",")[-1].split()[0]
        zip_code = address_raw[1].split(",")[-1].split()[-1]
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@class="tel"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall(r"LatLng\((.+)\);", loc_response.text)[0].split(",")[0]
        longitude = re.findall(r"LatLng\((.+)\);", loc_response.text)[0].split(",")[-1]
        hours_of_operation = loc_dom.xpath(
            '//strong[contains(text(), "Hours:")]/following::text()'
        )[1].strip()
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
