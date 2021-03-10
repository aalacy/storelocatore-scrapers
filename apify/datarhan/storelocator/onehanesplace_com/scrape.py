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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "onehanesplace.com"
    start_url = "https://outlets.onehanesplace.com/index.html"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
    for url in all_urls:
        if len(url.split("/")) == 3:
            all_locations.append(url)

        state_response = session.get(urljoin(start_url, url))
        state_dom = etree.HTML(state_response.text)
        all_locations += state_dom.xpath(
            '//a[@class="LocationCard-link LocationCard-link--page"]/@href'
        )
        state_urls = state_dom.xpath(
            '//a[@class="c-directory-list-content-item-link"]/@href'
        )
        for url in state_urls:
            if len(url.split("/")) == 3:
                all_locations.append(url)
            city_response = session.get(urljoin(start_url, url))
            city_dom = etree.HTML(city_response.text)
            all_locations += city_dom.xpath(
                '//a[@class="LocationCard-link LocationCard-link--page"]/@href'
            )

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        store_response = session.get(store_url)
        loc_dom = etree.HTML(store_response.text)

        location_name = " ".join(loc_dom.xpath('//h1[@id="location-name"]/span/text()'))
        street_address = loc_dom.xpath('//meta[@itemprop="streetAddress"]/@content')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = loc_dom.xpath('//abbr[@itemprop="addressCountry"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath('//tr[@itemprop="openingHours"]//text()')
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
        check = "{} {}".format(location_name, street_address)
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
