import re
import csv
from lxml import etree
from urllib.parse import urljoin
from w3lib.url import add_or_replace_parameter

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
    scraped_items = []

    DOMAIN = "henryford.com"
    start_url = "https://www.henryford.com/locations/search-results?services=&zip=&locationtype={}&locationname=&range=&page=1"
    response = session.get("https://www.henryford.com/locations/search-results")
    dom = etree.HTML(response.text)
    all_types = dom.xpath('//select[@name="locationtype"]/option/@value')[1:]
    for location_type in all_types:
        if location_type == "open locations":
            continue
        response = session.get(start_url.format(location_type.replace(" ", "+")))
        dom = etree.HTML(response.text)
        all_locations = dom.xpath('//div[@class="module-lc-info"]/h4/a/@href')
        total = dom.xpath('//div[@class="module-pg-info"]/text()')[0]
        total = int(re.findall(r"of (\d+) | Re", total)[0])
        for page in range(2, total + 1):
            response = session.get(
                add_or_replace_parameter(start_url, "page", str(page))
            )
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//div[@class="module-lc-info"]/h4/a/@href')

        for store_url in all_locations:
            store_url = urljoin(start_url, store_url)
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)

            location_name = store_dom.xpath('//div[@class="content"]/h1/text()')
            if not location_name:
                location_name = store_dom.xpath('//h1[@class="loc-detail-h1"]/text()')
                location_name = [location_name[0].strip()] if location_name else ""
            location_name = location_name[0] if location_name else "<MISSING>"
            street_address = store_dom.xpath('//span[@id="address1"]/text()')[0]
            if store_dom.xpath('//span[@id="address2"]/text()'):
                street_address += (
                    ", " + store_dom.xpath('//span[@id="address2"]/text()')[0]
                )
            city = store_dom.xpath('//span[@id="city"]/text()')
            city = city[0].replace(",", "") if city else "<MISSING>"
            state = store_dom.xpath('//span[@id="state"]/text()')
            state = state[0].strip() if state else "<MISSING>"
            zip_code = store_dom.xpath('//span[@id="zip"]/text()')
            zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = "<MISSING>"
            phone = store_dom.xpath('//div[@class="phones"]//a/text()')
            phone = phone[0] if phone else "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours_of_operation = "<INACCESSIBLE>"

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
