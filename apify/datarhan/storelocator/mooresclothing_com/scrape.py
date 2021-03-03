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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://stores.mooresclothing.com/index.html"
    domain = 'mooresclothing.com'
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = []
    all_urls = dom.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
    for url in all_urls:
        if "/" in url:
            all_locations.append(url)
            continue
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        sub_urls = dom.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
        for url in sub_urls:
            if len(url.split("/")) != 2:
                all_locations.append(url)
                continue
            response = session.get(urljoin(start_url, url))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@class="Link Teaser-link"]/@href')

    for url in all_locations:
        if "google" in url:
            continue
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h1[@class="LocationInfo-title"]/span[@itemprop="name"]/span[@class="LocationName-geo"]/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//address//span[@class="c-address-street-1 "]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = loc_dom.xpath("//@data-country")
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = loc_dom.xpath("//main/@itemtype")[0].split("/")[-1]
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath('//table[@class="c-location-hours-details"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo[2:]) if hoo else "<MISSING>"

        item = [
            domain,
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
