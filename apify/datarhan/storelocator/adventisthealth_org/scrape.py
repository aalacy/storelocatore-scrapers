import csv
from lxml import etree
from urllib.parse import urljoin

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
    scraped_items = []

    DOMAIN = "adventisthealth.org"
    start_url = "https://www.adventisthealth.org/locations/?lsearch=&TypeID=268"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath("//li[@itemscope]")
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//div[@class="info"]/a/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        location_name = poi_html.xpath("@data-name")
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = poi_html.xpath("@data-address")
        street_address = street_address[0] if street_address else "<MISSING>"
        if poi_html.xpath(".//address/span/text()"):
            street_address += ", " + poi_html.xpath(".//address/span/text()")[0]
        city = poi_html.xpath("@data-city")
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath("@data-state")
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath("@data-zip")
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi_html.xpath("@data-loc-id")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_html.xpath('.//p[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath(".//img/@src")[0].split("pin-")[-1].split("-")[0]
        latitude = poi_html.xpath("@data-latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
