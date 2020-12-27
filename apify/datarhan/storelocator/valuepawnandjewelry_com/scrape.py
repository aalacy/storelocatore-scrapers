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

    DOMAIN = "valuepawnandjewelry.com"
    start_url = "https://stores.valuepawnandjewelry.com/"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    states = dom.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
    for url in states:
        state_response = session.get(urljoin(start_url, url))
        state_dom = etree.HTML(state_response.text)
        all_urls = state_dom.xpath(
            '//a[@class="c-directory-list-content-item-link"]/@href'
        )
        for url in all_urls:
            if len(url.split("/")) == 3:
                all_locations.append(url)
                continue
            city_response = session.get(urljoin(start_url, url))
            city_dom = etree.HTML(city_response.text)
            all_locations += city_dom.xpath(
                '//h3[@class="c-location-grid-item-title"]/a/@href'
            )

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@itemprop="name"]/span/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//section[@id="location-info"]//span[@class="c-address-street-1"]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath(
            '//section[@id="location-info"]//span[@class="c-address-city"]/span/text()'
        )
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//abbr[@class="c-address-state"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@class="c-address-postal-code"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = loc_dom.xpath(
            '//abbr[@class="c-address-country-name c-address-country-us"]/text()'
        )
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = loc_dom.xpath("//main/@itemtype")[0].split("/")[-1]
        location_type = location_type if location_type else "<MISSING>"
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath('//tr[@itemprop="openingHours"]/td//text()')
        hours_of_operation = (
            ", ".join(hours_of_operation).replace("  ", " ")
            if hours_of_operation
            else "<MISSING>"
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
