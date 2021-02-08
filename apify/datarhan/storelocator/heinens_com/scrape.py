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

    DOMAIN = "heinens.com"
    start_urls = [
        "https://www.heinens.com/stores/?state=IL",
        "https://www.heinens.com/stores/?state=OH",
    ]
    all_locations = []
    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//h2/a[contains(@href, "/stores/")]/@href')
        next_page = dom.xpath('//a[@class="next page-numbers"]/@href')
        while next_page:
            response = session.get(next_page[0])
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//h2/a[contains(@href, "/stores/")]/@href')
            next_page = dom.xpath('//a[@class="next page-numbers"]/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="page-title"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//meta[@itemprop="addressLocality"]/@content')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//meta[@itemprop="addressRegion"]/@content')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//meta[@itemprop="postalCode"]/@content')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@class="datum phone"]//a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath('//div[@class="datum hours"]//text()')
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
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
