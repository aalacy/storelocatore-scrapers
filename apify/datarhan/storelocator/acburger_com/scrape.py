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

    DOMAIN = "acburger.com"
    start_url = "https://acburger.com/locations.html?showall"

    state_response = session.get(start_url)
    dom = etree.HTML(state_response.text)
    all_locations = dom.xpath('//li[contains(@class, "loc")]')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h4/a/@href")
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath(".//h4/a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = poi_html.xpath(
            './/p[@class="btn-menu"]/following-sibling::p[1]/text()'
        )
        if not address_raw:
            continue
        street_address = address_raw[0]
        city = address_raw[1].split(", ")[0]
        state = address_raw[1].split(", ")[-1].split()[0]
        zip_code = address_raw[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = address_raw[-1].split(": ")[-1].strip()
        phone = phone if phone else "<MISSING>"
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
