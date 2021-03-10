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

    DOMAIN = "crevier.ca"
    start_url = "https://petroleum.crevier.ca/stations"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="box-station"]')
    for poi_html in all_locations:
        store_url = "<MISSING>"
        location_name = poi_html.xpath(".//h2/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = [
            elem.strip()
            for elem in poi_html.xpath('.//ul[@class="list-full"]/li/text()')
        ]
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = raw_address[1].split(",")[-1].strip()
        country_code = "<MISSING>"
        store_number = poi_html.xpath("@data-id")[0]
        phone = poi_html.xpath(".//a/text()")[-1]
        location_type = poi_html.xpath('.//ul[@class="row-full list-squared"]//text()')
        location_type = [elem.strip() for elem in location_type if elem.strip()]
        location_type = ", ".join(location_type) if location_type else "<MISSING>"
        latitude = poi_html.xpath("@data-latitude")[0]
        longitude = poi_html.xpath("@data-longitude")[0]
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
