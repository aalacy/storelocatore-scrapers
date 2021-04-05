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
    start_url = "https://www.coffeeculturecafe.com/find-your-location/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[contains(@id, "cc-location")]')
    for poi_html in all_locations:
        store_url = "https://www.coffeeculturecafe.com/find-your-location/"
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="store-name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//div[@class="store-address"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//div[@class="store-city"]/text()')[0].split(", ")[0]
        state = poi_html.xpath('.//div[@class="store-city"]/text()')[0].split(", ")[1]
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        if (
            "USA"
            in poi_html.xpath('.//div[@class="store-city"]/text()')[0].split(", ")[-1]
        ):
            country_code = "USA"
        store_number = poi_html.xpath("@id")[0].split("-")[-1]
        phone = poi_html.xpath('.//div[@class="store-phone"]/text()')[0].split(": ")[-1]
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="store-hours"]/text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
