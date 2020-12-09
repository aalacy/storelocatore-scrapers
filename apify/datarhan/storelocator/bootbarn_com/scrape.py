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

    DOMAIN = "bootbarn.com"
    start_url = "https://www.bootbarn.com/stores-all"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_stores = dom.xpath('//div[@class="store"]/div/a/@href')
    for url in all_stores:
        store_url = "https://www.bootbarn.com" + url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//h1[@class="section-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = store_dom.xpath(
            '//div[@class="store-info-left"]//span[@class="store-address1"]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = store_dom.xpath(
            '//div[@class="store-info-left"]//span[@class="store-address-city"]/text()'
        )
        city = city[0].replace(",", "") if city else "<MISSING>"
        state = store_dom.xpath(
            '//div[@class="store-info-left"]//span[@class="store-address-state"]/text()'
        )
        state = state[0] if state else "<MISSING>"
        zip_code = store_dom.xpath(
            '//div[@class="store-info-left"]//span[@class="store-address-postal-code"]/text()'
        )
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = store_url.split("=")[-1]
        phone = store_dom.xpath(
            '//div[@class="store-info-left"]//span[@class="store-phone"]/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = store_dom.xpath('//div[@id="store-detail-coords"]/@data-lat')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath('//div[@id="store-detail-coords"]/@data-lon')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath('//div[@class="store-hours-days"]//text()')
        hours_of_operation = [elem.strip() for elem in hours_of_operation if elem.strip]
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
