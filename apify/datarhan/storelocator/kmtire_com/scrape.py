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

    DOMAIN = "kmtire.com"
    start_url = "http://kmtire.com/km-cgi/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="locations-content"]/h5')

    for poi_html in all_locations:
        store_url = "http://kmtire.com/km-cgi/locations"
        location_name = poi_html.xpath("text()")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = poi_html.xpath(".//following-sibling::p[1]/text()")
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        if len(raw_address) == 5:
            raw_address = [", ".join(raw_address[:2])] + raw_address[2:]
        if not raw_address:
            continue
        street_address = raw_address[0].strip()
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_address[2].split(": ")[-1]
        location_type = "<MISSING>"
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
