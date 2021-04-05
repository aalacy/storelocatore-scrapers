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
    items = []

    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    DOMAIN = "totalaccessurgentcare.com"
    start_url = "https://www.totalaccessurgentcare.com/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)

    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//ul[@data-role="results"]/li')

    for poi_html in all_locations:
        store_url = poi_html.xpath('.//span[@itemprop="name"]/a/@href')
        if not store_url:
            continue
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        location_name = poi_html.xpath('.//span[@itemprop="name"]/a/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath("@data-address")
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath("@data-city")
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath("@data-state")
        state = state[0] if state else "<MISSING>"
        zip_code = poi_html.xpath("@data-zip")
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi_html.xpath("@data-loc-id")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = poi_html.xpath("@data-phone")
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath("@itemtype")[0].split("/")[-1]
        latitude = poi_html.xpath("@data-latitude")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = poi_html.xpath("@data-longitude")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = etree.HTML(poi_html.xpath("@data-hours")[0])
        if hours_of_operation:
            hours_of_operation = hours_of_operation.xpath("//text()")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            location_type = "coming soon"

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
