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
    session = SgRequests()

    items = []

    DOMAIN = "henryford.com"
    start_url = "https://www.henryford.com/locations/search-results?services=&zip=&locationtype=&locationname=&range=&page=1"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="module-lc-info"]/h4/a/@href')
    total = dom.xpath('//div[@class="module-pg-info"]/text()')[0]
    total = int(re.findall(r"of (\d+) | Re", total)[0])
    for page in range(2, total + 1):
        response = session.get(add_or_replace_parameter(start_url, "page", str(page)))
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
            street_address += ", " + store_dom.xpath('//span[@id="address2"]/text()')[0]
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
        location_type = "Hospital"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = []
        hoo = store_dom.xpath(
            '//h4[contains(text(), "Hours")]/following-sibling::ul//text()'
        )
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        for elem in hoo:
            if ("Fax" and "Phone" and "Please") in elem:
                continue
            hours_of_operation.append(elem)
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        if "00 p.m" not in hours_of_operation:
            hours_of_operation = "<MISSING>"
        if hours_of_operation != "<MISSING>":
            hours_of_operation = "Monday" + hours_of_operation.split("Monday")[-1]
            hours_of_operation = hours_of_operation.strip()
            if not hours_of_operation.endswith("p.m."):
                hours_of_operation = "p.m. ".join(
                    hours_of_operation.split("p.m. ")[:-1]
                )
        hours_of_operation = (
            hours_of_operation.strip() if hours_of_operation.strip() else "<MISSING>"
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
