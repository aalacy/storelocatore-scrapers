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

    session = SgRequests()

    DOMAIN = "tirediscounters.com"
    start_url = "https://locations.tirediscounters.com/index.html"
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_urls = []
    states_urls = dom.xpath('//a[@class="Directory-listLink"]/@href')
    for state_url in states_urls:
        state_response = session.get(urljoin(start_url, state_url))
        state_dom = etree.HTML(state_response.text)
        all_urls += state_dom.xpath('//a[@class="Teaser-titleLink"]/@href')

    for url in all_urls:
        store_url = urljoin(start_url, url)
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//span[@id="location-name"]/span/text()')
        location_name = " ".join(location_name) if location_name else "<MISSING>"
        street_address = store_dom.xpath('//meta[@itemprop="streetAddress"]/@content')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = store_dom.xpath('//span[@class="c-address-city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = store_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = store_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = store_dom.xpath('//abbr[@itemprop="addressCountry"]/text()')[0]
        store_number = "<MISSING>"
        phone = store_dom.xpath('//div[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = store_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = store_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = store_dom.xpath(
            '//table[@class="c-hours-details"]//text()'
        )[2:]
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
