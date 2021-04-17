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

    DOMAIN = "bravoitalian.com"
    start_url = "https://locations.bravoitalian.com/us"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = []
    all_urls = dom.xpath('//div[@class="c-directory-list"]//a/@href')
    for url in all_urls:
        if len(url) != 5:
            all_locations.append(url)
            continue
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_sub_urls = dom.xpath('//div[@class="c-directory-list"]//a/@href')
        for url in all_sub_urls:
            if len(url.split("/")) != 4:
                all_locations.append(url)
                continue

            response = session.get(urljoin(start_url, url))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@data-ya-track="visit_page"]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h1[@itemprop="name"]//span[@class="LocationName-geo"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//div[@class="Nap-addressHoursWrapper"]//span[@class="c-address-street-1 "]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath(
            '//div[@class="Nap-addressHoursWrapper"]//span[@itemprop="addressLocality"]/text()'
        )
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath(
            '//div[@class="Nap-addressHoursWrapper"]//span[@itemprop="addressRegion"]/text()'
        )
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath(
            '//div[@class="Nap-addressHoursWrapper"]//span[@itemprop="postalCode"]/text()'
        )
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = loc_dom.xpath('//abbr[@itemprop="addressCountry"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@id="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//div[@class="Nap-addressHoursWrapper"]//table[@class="c-location-hours-details"]//text()'
        )[2:]
        hours_of_operation = [elem.strip() for elem in hours_of_operation]
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
