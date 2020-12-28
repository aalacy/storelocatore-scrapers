import csv
import json
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

    DOMAIN = "chanellospizza.com"
    start_url = "https://chanellospizza.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    city_dict = {}
    all_cities = dom.xpath('//div[@class="area-location"]')
    for city in all_cities:
        city_name = city.xpath(".//h1/text()")[0]
        loc_names = city.xpath('.//div[@class="location-item"]/strong/text()')
        for loc_name in loc_names:
            city_dict[loc_name.replace("’s", "s")] = city_name

    data = dom.xpath('//div[@class="map"]/@data-markers')[0]
    data = json.loads(data)

    for poi in data:
        poi_html = etree.HTML(poi["popup"])

        store_url = poi_html.xpath('.//div[@class="online-order"]/a/@href')[0]
        location_name = poi["title"].replace("&#8217;", "")
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi_html.xpath(".//address/text()")
        street_address = street_address[0] if street_address else "<MISSING>"
        city = city_dict[location_name]
        state = "<MISSING>"
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi_html.xpath('.//a[contains(@href, "tel")]/@href')
        phone = phone[0].split(":")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"][0]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["location"][-1]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi_html.xpath('.//ul[@class="working-hours"]/li/text()')
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
