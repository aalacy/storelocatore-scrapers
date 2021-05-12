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

    DOMAIN = "coffeeculturecafe.com"
    start_url = "https://www.coffeeculturecafe.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//section[contains(@data-settings, "ekit_has_onepagescroll_dot")]/div/div[@data-element_type="column"]'
    )
    for poi_html in all_locations:
        store_url = start_url
        location_name = poi_html.xpath(".//p/span/strong/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = poi_html.xpath(
            './/div[@class="elementor-text-editor elementor-clearfix"]/p[2]/text()'
        )
        raw_data = [e.strip() for e in raw_data if e.strip()]
        if not raw_data:
            continue
        street_address = raw_data[0]
        city = location_name.split(",")[0].strip()
        state = location_name.split(",")[-1].strip()
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = raw_data[1].split(":")[-1].strip()
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = raw_data[-1]

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
