import csv
import json
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
    scraped_items = []

    DOMAIN = "itsugar.com"
    start_url = "https://itsugar.com/amlocator/index/ajax/"
    formdata = {
        "lat": "0",
        "lng": "0",
        "radius": "0",
        "product": "0",
        "category": "0",
        "sortByDistance": "1",
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.post(start_url, data=formdata, headers=headers)
    data = json.loads(response.text)

    for poi in data["items"]:
        poi_html = etree.HTML(poi["popup_html"])
        store_url = poi_html.xpath('//a[@class="amlocator-link"]/@href')
        store_url = store_url[0] if store_url else "<MISSING>"
        raw_state = poi_html.xpath("//text()")
        raw_state = [elem.strip() for elem in raw_state if elem.strip()]
        location_name = poi_html.xpath('//a[@class="amlocator-link"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = raw_state[1]
        city = raw_state[2].split(", ")[0]
        state = raw_state[2].split(", ")[1]
        zip_code = raw_state[2].split(", ")[2]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = raw_state[3]
        if "AM" in phone:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = raw_state[-1]

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
        if store_url not in scraped_items:
            scraped_items.append(store_url)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
