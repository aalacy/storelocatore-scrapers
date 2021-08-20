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

    DOMAIN = "brownschicken.com"
    start_url = "https://www.brownschicken.com/locator.php"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="buttonFrame store"]')
    for poi_html in all_locations:
        store_url = "https://www.brownschicken.com/locator.php"
        location_name = poi_html.xpath(".//b/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath("text()")[-2:]
        raw_address = [e.strip() for e in raw_address]
        street_address = raw_address[0]
        city = raw_address[-1].split(", ")[0]
        state = raw_address[-1].split(", ")[-1].split()[0]
        zip_code = raw_address[-1].split(", ")[-1].split()[-1]
        country_code = re.findall("countrycodes=(.+)'", response.text)[0]
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi_html.xpath('.//div[@class="orderNow comingSoon"]'):
            location_type = "Coming Soon"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
