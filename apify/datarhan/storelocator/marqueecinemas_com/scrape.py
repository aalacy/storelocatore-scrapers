import csv
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "marqueecinemas.com"
    start_url = "https://www.marqueecinemas.com/locations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="nounderline"]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@id="showtimes_wrapper"]/h2/span//text()')
        location_name = " ".join(location_name) if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//span[@class="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        addr = parse_address_intl(" ".join(raw_address[:-1]))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_2
        city = addr.city
        state = addr.state
        zip_code = addr.postcode
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_address[-1].split(":")[-1].strip()
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
