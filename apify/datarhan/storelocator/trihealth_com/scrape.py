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

    DOMAIN = "trihealth.com"
    start_url = "https://www.trihealth.com/hospitals-and-practices/"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//table[@dropzone="copy"]//ul/li/a/@href')
    for url in all_locations:
        store_url = url
        if "http" not in url:
            store_url = "https://www.trihealth.com" + url
        if "cgha.com" in url:
            continue
        print(store_url)
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//div[@id="subhead"]/h1/text()')
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        street_address = store_dom.xpath('//span[@class="street-address"]/text()')
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        city = store_dom.xpath('//span[@class="locality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = store_dom.xpath('//span[@class="region"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = store_dom.xpath('//span[@class="postal-code"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = store_dom.xpath(
            '//div[@class="tel subtle"]/span/span[@class="hidden-xs hidden-sm"]/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
