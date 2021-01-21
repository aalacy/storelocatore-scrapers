import csv
import json
from urllib.parse import urljoin
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

    DOMAIN = "westmarine.com"

    start_url = "https://www.westmarine.com/store-finder"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="store-content"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath("./li[1]/a/@href")
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        location_name = poi_html.xpath("./li[1]/a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath("./li[2]/text()")
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath("./li[3]/text()")[0].split(",")[0]
        city = city if city else "<MISSING>"
        state = poi_html.xpath("./li[3]/text()")
        state = state[0].split(",")[-1].strip() if state else "<MISSING>"
        zip_code = poi_html.xpath("./li[4]/text()")
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath("./li[5]/text()")
        phone = phone[0] if phone else "<MISSING>"

        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        poi_data = loc_dom.xpath('//script[contains(text(), "openingHours")]/text()')[0]
        poi_data = json.loads(poi_data)
        country_code = poi_data["address"]["addressCountry"]
        location_type = poi_data["@type"]
        latitude = poi_data["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi_data["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi_data["openingHours"]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        hours_of_operation = hours_of_operation.replace("  ", " closed ")
        if hours_of_operation.endswith(" "):
            hours_of_operation = hours_of_operation + "closed"

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
