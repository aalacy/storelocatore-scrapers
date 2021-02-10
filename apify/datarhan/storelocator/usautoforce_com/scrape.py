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

    DOMAIN = "usautoforce.com"
    start_url = "http://www.usautoforce.com/about/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[@data-id]")
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//div[@class="larger uppercase"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        address_raw = poi_html.xpath('.//div[@class="map-location-button"]/div/text()')[
            1:
        ]
        city = address_raw[-1].split(", ")[0]
        street_address = address_raw[0]
        state = address_raw[-1].split(", ")[-1].split()[0]
        zip_code = address_raw[-1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        if poi_html.xpath("@class")[0].endswith("red"):
            location_type = "Tire's Warehouse"
        else:
            location_type = "U.S. AutoForce"
        store_number = "<MISSING>"
        phone = "<MISSING>"
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
