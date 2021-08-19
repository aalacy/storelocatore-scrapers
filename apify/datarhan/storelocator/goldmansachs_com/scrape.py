import re
import csv
from lxml import etree

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

    start_url = "https://www.goldmansachs.com/our-firm/locations.html"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//ul[@class="listings filter"]/li')
    for poi_html in all_locations:
        country_code = poi_html.xpath('.//span[@class="country"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        if country_code not in ["Canada", "United Kingdom", "United States"]:
            continue
        store_url = start_url
        location_name = poi_html.xpath('.//span[@class="address"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//span[@class="address"]/text()')[1:]
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(" ".join(raw_address) + " " + country_code)
        if not addr.street_address_1:
            raw_address = poi_html.xpath('.//span[@class="address"]/text()')
            location_name = "<MISSING>"
            addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if street_address and addr.street_address_2:
            street_address += " " + addr.street_address_2
        else:
            street_address = addr.street_address_2
        if not street_address:
            if country_code in ["Canada", "United Kingdom"]:
                street_address = ", ".join(raw_address[:2])
            else:
                street_address = raw_address[0]
        street_address = street_address if street_address else "<MISSING>"
        city = poi_html.xpath('.//span[@class="city"]/text()')
        city = city[0].split(",")[0] if city else "<MISSING>"
        state = addr.state
        state = state.replace(".", "") if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi_html.xpath('.//span[@class="phone"]/span/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

        if street_address == "Suite 1000 East":
            street_address = f"{location_name} {street_address}"
            location_name = "<MISSING>"

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
