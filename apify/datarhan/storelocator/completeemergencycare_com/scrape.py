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

    start_url = "https://www.visitcompletecare.com/er-locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@itemscope="itemscope"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath('.//span[@itemprop="name"]/a/@href')[0]
        store_url = urljoin(start_url, store_url)
        location_name = poi_html.xpath('.//span[@itemprop="name"]/a/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = poi_html.xpath('.//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = poi_html.xpath('.//span[@itemprop="addressRegion"]/text()')
        state = state[0].strip() if state else "<MISSING>"
        zip_code = poi_html.xpath('.//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0].strip() if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//span[@itemprop="telephone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = poi_html.xpath("@itemtype")[0].split("/")[-1]
        geo = (
            poi_html.xpath('.//span[@class="ftr-mapus"]/a/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        latitude = geo[0]
        longitude = geo[1]
        hours_of_operation = "<MISSING>"

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
