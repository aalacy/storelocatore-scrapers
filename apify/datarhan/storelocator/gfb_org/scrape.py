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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "gfb.org"
    start_url = "https://www.gfb.org/about-us/contact-us.cms"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath("//div[@data-county]")

    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(".//h2//text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = poi_html.xpath(
            './/h3[contains(text(), "Street Address")]/following-sibling::p/text()'
        )
        address_raw = [elem.strip() for elem in address_raw]
        street_address = address_raw[1]
        city = address_raw[2].split()[0]
        state = address_raw[2].split()[-1]
        zip_code = address_raw[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(
            './/h3[contains(text(), "Phone")]/following-sibling::p[1]/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = poi_html.xpath(
            './/h3[contains(text(), "Hours")]/following-sibling::p[1]/text()'
        )[0].strip()

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
