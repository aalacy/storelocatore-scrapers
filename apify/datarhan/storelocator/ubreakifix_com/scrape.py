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

    DOMAIN = "ubreakifix.com"

    start_url = "https://www.ubreakifix.com/locations"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_urls = dom.xpath('//div[@id="storelist"]//a/@href')
    canadian_url = "https://www.ubreakifix.com/ca/locations"
    ca_response = session.get(canadian_url)
    ca_dom = etree.HTML(ca_response.text)
    all_urls += ca_dom.xpath('//div[@id="storelist"]//a/@href')
    for url in all_urls[1:]:
        if "#" in url:
            continue
        if "https" in url:
            continue
        full_store_url = "https://www.ubreakifix.com/" + url
        store_response = session.get(full_store_url)
        store_dom = etree.HTML(store_response.text)

        store_url = full_store_url
        location_name = store_dom.xpath('//h1[@class="title"]/text()')
        location_name = (
            " ".join(location_name[0].strip().split()) if location_name else "<MISSING>"
        )
        street_address = store_dom.xpath('//meta[@itemprop="streetAddress"]/@content')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = store_dom.xpath('//meta[@itemprop="addressLocality"]/@content')
        city = city[0] if city else "<MISSING>"
        state = store_dom.xpath('//meta[@itemprop="addressRegion"]/@content')
        state = state[0] if state else "<MISSING>"
        zip_code = store_dom.xpath('//meta[@itemprop="postalCode"]/@content')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = store_dom.xpath('//meta[@itemprop="addressCountry"]/@content')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = ""
        store_number = store_number if store_number else "<MISSING>"
        phone = store_dom.xpath(
            '//div[@class="content-group"]//a[contains(@href, "tel")]/text()'
        )
        phone = phone[0].strip() if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = store_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath(
            '//meta[@itemprop="openingHours"]/@content'
        )
        hours_of_operation = (
            hours_of_operation[0] if hours_of_operation else "<MISSING>"
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
