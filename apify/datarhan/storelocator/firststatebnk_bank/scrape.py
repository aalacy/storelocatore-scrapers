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

    start_url = "https://www.firststatebnk.bank/locations-and-hours/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "Branch Details")]/@href')
    for store_url in all_locations:
        store_url = urljoin(start_url, store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//*[@itemprop="name"]/text()')[0]
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        if not street_address:
            street_address = loc_dom.xpath('//p[@class="location"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')[0]
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')[0]
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')[0]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
        if not phone:
            phone = loc_dom.xpath('//p[@class="phone"]/span/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath('//a[contains(@href, "maps/place")]/@href')[0]
            .split("/@")[-1]
            .split(",")[:2]
        )
        latitude = geo[0]
        longitude = geo[1]
        hoo = loc_dom.xpath(
            '//h4[contains(text(), "Lobby Hours")]/following-sibling::table//text()'
        )
        hoo = [e.strip() for e in hoo if e.strip()]
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
