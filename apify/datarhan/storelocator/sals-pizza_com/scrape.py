import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://sals-pizza.com/locations"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@data-block-type="2"]')[2:]
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//following-sibling::div[1]//a/@href")
        store_url = (
            store_url[0]
            if store_url and ".pdf" not in store_url[0].lower()
            else start_url
        )
        location_name = poi_html.xpath(".//h2/strong/text()")
        if not location_name:
            location_name = poi_html.xpath(
                './/div[@class="sqs-block-content"]/h2/text()'
            )
        if not location_name:
            continue
        location_name = location_name[0]
        street_address = poi_html.xpath(".//p/text()")
        street_address = street_address[0] if street_address else "<MISSING>"
        city = location_name.split(", ")[0]
        state = location_name.split(", ")[-1]
        zip_code = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath(".//p/strong/text()")
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi_html.xpath('.//h3/strong[contains(text(), "currently closed")]'):
            location_type = "currently closed"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        item = [
            domain,
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
