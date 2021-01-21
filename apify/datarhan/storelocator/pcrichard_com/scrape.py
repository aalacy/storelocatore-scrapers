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

    DOMAIN = "pcrichard.com"
    start_url = "https://www.pcrichard.com/storelocator/store-landing.jsp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
    }

    response = session.get(start_url, headers=headers, verify=False)
    dom = etree.HTML(response.text)
    all_urls = dom.xpath('//div[@class="ministore_links"]//a/@href')

    for url in all_urls:
        store_url = urljoin(start_url, url)
        store_response = session.get(store_url, headers=headers, verify=False)
        store_dom = etree.HTML(store_response.text)

        location_name = store_dom.xpath('//h1[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = store_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = store_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = store_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = store_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = store_dom.xpath("//@data-country")
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = store_dom.xpath("//div/@store")
        store_number = store_number[0] if store_number else "<MISSING>"
        phone = store_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = store_dom.xpath("//div/@itemtype")[0].split("/")[-1]
        geo = re.findall(
            "!2d(.+?)!2m", store_dom.xpath('//div[@itemprop="hasMap"]/iframe/@src')[0]
        )[0].split("!3d")
        latitude = geo[1]
        longitude = geo[0]
        hours_of_operation = "<INACCESSIBLE>"

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
