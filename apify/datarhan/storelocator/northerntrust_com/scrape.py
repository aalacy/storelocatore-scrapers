import re
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

    start_url = "https://locations.northerntrust.com/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@data-count="(1)"]/@href')
    urls = dom.xpath('//a[@data-count!="(1)"]/@href')
    for url in urls:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[@data-count="(1)"]/@href')
        more_urls = dom.xpath('//a[@data-count!="(1)"]/@href')
        for url in more_urls:
            response = session.get(urljoin(start_url, url))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[@data-count="(1)"]/@href')
            final_urls = dom.xpath('//a[@data-count!="(1)"]/@href')
            for url in final_urls:
                response = session.get(urljoin(start_url, url))
                dom = etree.HTML(response.text)
                all_locations += dom.xpath('//a[@class="Teaser-titleLink"]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="Hero-locationTitle"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//address//span[@class="c-address-street-1"]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        street_2 = loc_dom.xpath('//span[@class="c-address-street-2"]/text()')
        if street_2:
            street_address += " " + street_2[0]
        city = loc_dom.xpath('//address//span[@class="c-address-city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//abbr[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//address//div[@id="phone-main"]/text()')
        phone = phone[0].replace("Call", "") if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath('//meta[@itemprop="latitude"]/@content')[0]
        longitude = loc_dom.xpath('//meta[@itemprop="longitude"]/@content')[0]
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "Lobby Banking Hours")]/following-sibling::div[2]//table[@class="c-hours-details"]//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()][2:]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
