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
    items = []

    session = SgRequests()

    DOMAIN = "superdry.com"
    start_urls = ["https://stores.superdry.com/gb", "https://stores.superdry.com/us"]

    all_locations = []
    for start_url in start_urls:
        response = session.get(start_url)
        dom = etree.HTML(response.text)
        all_urls = dom.xpath('//a[@class="Directory-listLink"]/@href')
        for url in all_urls:
            url = urljoin(start_url, url)
            if "/gb/" in url and len(url.split("/")) > 5:
                all_locations.append(url)
                continue
            elif "/us/" in url and len(url.split("/")) > 6:
                all_locations.append(url)
                continue
            city_response = session.get(urljoin(start_url, url))
            city_dom = etree.HTML(city_response.text)
            all_locations += city_dom.xpath('//a[@class="Teaser-titleLink"]/@href')
            sub_urls = city_dom.xpath('//a[@class="Directory-listLink"]/@href')
            for url in sub_urls:
                url = urljoin(start_url, url)
                if "/gb/" in url and len(url.split("/")) > 5:
                    all_locations.append(url)
                    continue
                elif "/us/" in url and len(url.split("/")) > 6:
                    all_locations.append(url)
                    continue
                sub_response = session.get(urljoin(start_url, url))
                sub_dom = etree.HTML(sub_response.text)
                all_locations += sub_dom.xpath('//a[@class="Teaser-titleLink"]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        print(store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1/span[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@class="c-address-street-1"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@class="c-address-city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = loc_dom.xpath('//abbr[@itemprop="addressCountry"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//div[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath('//table[@class="c-hours-details"]//text()')[2:16]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
