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

    DOMAIN = "simmonsbakers.com"
    start_url = "https://www.simmonsbakers.com/shops"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//div[@itemscope]")
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath('.//div[@itemprop="name"]/text()')
        if not location_name:
            continue
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@itemprop="streetAddress"]/text()')
        street_address = " ".join(street_address) if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//a[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath("@itemtype")[0].split("/")[-1]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = poi_html.xpath(".//time/@datetime")
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
