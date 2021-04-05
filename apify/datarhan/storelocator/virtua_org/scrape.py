import csv
from urllib.parse import urljoin
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

    DOMAIN = "virtua.org"
    start_url = "https://www.virtua.org/locations/search-results"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@class="search-listing-item__text-content"]/h3/a/@href'
    )
    next_page = dom.xpath('//li[@class="pagination_button next-btn "]/a/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//div[@class="search-listing-item__text-content"]/h3/a/@href'
        )
        next_page = dom.xpath('//li[@class="pagination_button next-btn "]/a/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        if not loc_dom.xpath("//@data-map-coords"):
            continue

        location_name = loc_dom.xpath('//h1[@itemprop="name"]/text()')
        location_name = (
            location_name[0].split(" - ")[0] if location_name else "<MISSING>"
        )
        street_address = loc_dom.xpath('//p[@itemprop="streetAddress"]/text()')
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0].strip() if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-map-coords")[0].split(",")[0]
        longitude = loc_dom.xpath("//@data-map-coords")[0].split(",")[-1]
        hours_of_operation = loc_dom.xpath(
            '//h3[contains(text(), "Hours")]/following-sibling::div[1][@class="accordion-content rta"]/div[1]//text()'
        )
        hours_of_operation = [
            elem.strip() for elem in hours_of_operation if elem.strip()
        ]
        hours_of_operation = (
            ", ".join(hours_of_operation)
            .split("visiting is")[0]
            .replace("Although ", "")
        )
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
