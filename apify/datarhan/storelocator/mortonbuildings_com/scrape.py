import re
import csv
import demjson
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "mortonbuildings.com"
    start_url = "https://mortonbuildings.com/locations"

    response = session.get(start_url)
    all_locations = re.findall(
        r'(\{"maxWidth":300,"content":".+?)\);', response.text.replace("\n", "")
    )

    for poi_html in all_locations:
        poi_html = demjson.decode(poi_html)
        poi_html = etree.HTML(
            poi_html["content"]
            .replace("\n", "")
            .replace("&lt;", "<")
            .replace("&#039;", '"')
            .replace("&gt;", ">")
        )

        store_url = poi_html.xpath('//a[contains(text(), "More Details")]/@href')[0]
        location_name = poi_html.xpath(".//div/@data-city-state")[0]
        location_name = ", ".join(
            [elem.capitalize() for elem in location_name.split(", ")]
        )
        street_address = poi_html.xpath(".//address/text()")
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        city = poi_html.xpath(".//address/text()")[-1].split(", ")[0]
        city = city.strip() if city else "<MISSING>"
        state = poi_html.xpath(".//address/text()")[-1].split(", ")[-1]
        state = state.strip().split()[0] if state else "<MISSING>"
        zip_code = poi_html.xpath(".//@data-zip")[0]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi_html.xpath(".//@data-lat")[0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi_html.xpath(".//@data-lng")[0]
        longitude = longitude if longitude else "<MISSING>"
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
