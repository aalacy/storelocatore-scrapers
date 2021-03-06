import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    start_url = "https://www.roxberryjuice.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    data = re.findall("et_link_options_data = (.+);", response.text)[0]
    data = json.loads(data)

    all_locations = [e["url"] for e in data]
    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="et_pb_module_header"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@itemprop="address"]/text()')
        street_address = (
            " ".join([e.strip() for e in street_address])
            if street_address
            else "<MISSING>"
        )
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        if street_address == "<MISSING>":
            raw_address = loc_dom.xpath(
                '//div[p[contains(text(), "ROXBERRY")]]/p/text()'
            )
            if not raw_address:
                raw_address = loc_dom.xpath(
                    '//div[p[contains(text(), "Roxberry")]]/p/text()'
                )
                if len(raw_address) == 1:
                    raw_address = None
            if raw_address and "Pleasant Grove was recently" in raw_address[0]:
                raw_address = None
            if not raw_address:
                raw_address = loc_dom.xpath(
                    '//div[p[strong[contains(text(), "Roxberry")]]]/p/text()'
                )
            raw_address = [e.strip() for e in raw_address if e.strip()]
            addr = parse_address_intl(" ".join(raw_address))
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            city = city if city else "<MISSING>"
            state = addr.state
            state = state if state else "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
