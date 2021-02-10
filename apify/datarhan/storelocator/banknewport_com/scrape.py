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

    DOMAIN = "banknewport.com"
    start_url = "https://www.banknewport.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[@class="locations active"]//div[@class="location"]'
    )
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//a[@class="name"]/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//a[@class="name"]/text()')
        location_name = location_name[-1].strip() if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//p[@class="address"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//p[@class="address"]/text()')[-1].split(", ")[0]
        state = (
            poi_html.xpath('.//p[@class="address"]/text()')[-1]
            .split(", ")[-1]
            .split()[0]
        )
        zip_code = (
            poi_html.xpath('.//p[@class="address"]/text()')[-1]
            .split(", ")[-1]
            .split()[-1]
        )
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[@class="phone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath('.//div[@class="hours"]/p[2]//text()')
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if "fax" in hours_of_operation.lower():
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
