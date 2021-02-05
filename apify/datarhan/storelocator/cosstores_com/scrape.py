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

    DOMAIN = "cosstores.com"
    start_url = "https://www.cosstores.com/ca/en/store-locator/united-states/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="store"]')
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(".//h2/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath(".//p/text()")[:4]
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        street_address = raw_address[0].split(", ")[0]
        city = raw_address[0].split(", ")[-1]
        state = raw_address[2].split()[-1]
        zip_code = raw_address[2].split()[0]
        country_code = raw_address[-1].strip()
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//p/text()")[4].split(": ")[-1]
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
