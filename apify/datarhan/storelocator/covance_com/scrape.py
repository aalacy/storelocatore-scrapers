import csv
from lxml import etree

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
    scraped_items = []

    DOMAIN = "covance.com"
    start_url = "https://www.covance.com/locations.html"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="locations-results-row"]')

    for poi_html in all_locations[1:]:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//li[@class="name"]/text()')
        if not location_name:
            continue
        location_name = (
            location_name[0].replace("<", "") if location_name else "<MISSING>"
        )
        raw_address = poi_html.xpath('.//li[@class="address"]/text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        full_addr = " ".join(raw_address).replace("\n", " ").replace("\t", " ")
        addr = parse_address_intl(full_addr)
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + addr.street_address_1
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//li[@class="phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
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
        check = f"{street_address} {city}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
