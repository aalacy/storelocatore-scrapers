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

    start_url = "https://www.ccscoffee.com/locations"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View more details")]/@href')
    for store_url in all_locations:
        if "http" not in store_url:
            continue

        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath('//div[@class="location__dtl"]/a/text()')[0]
        addr = parse_address_intl(raw_address)
        location_name = loc_dom.xpath('//h1[@class="h1"]/text()')[0].strip()
        street_address = raw_address.split(", ")[0]
        city = addr.city
        if "Broussard" in raw_address:
            city = "Broussard"
        if "Lafayette" in raw_address:
            city = "Lafayette"
        if "Metairie" in raw_address:
            city = "Metairie"
        if "Pineville" in raw_address:
            city = "Pineville"
        state = addr.state
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//b[contains(text(), "Phone")]/following-sibling::span/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-latitude")[0]
        longitude = loc_dom.xpath("//@data-longitude")[0]
        hoo = loc_dom.xpath(
            '//b[contains(text(), "Hours of Operation")]/following-sibling::ul//text()'
        )
        hoo = [e.strip().replace("\n", "") for e in hoo if e.strip()]
        if not hoo:
            location_type = "TEMPORARILY CLOSED"
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
