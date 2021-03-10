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

    start_url = "https://fitnessfor10.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = []
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    all_regions = dom.xpath('//a[@class="w-btn us-btn-style_1"]/@href')
    for url in all_regions:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[span[contains(text(), "Click Here")]]/@href')

    for store_url in all_locations:
        if "fitnessfor10.com" not in store_url:
            continue

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_addresss = loc_dom.xpath(
            '//h5[contains(text(), "ADDRESS")]/following-sibling::div/*/text()'
        )
        addr = parse_address_intl(" ".join(raw_addresss))
        location_name = loc_dom.xpath('//h2[@itemprop="headline"]/text()')
        if not location_name:
            location_name = loc_dom.xpath("//title/text()")[0].split(",")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//h5[contains(text(), "ADDRESS")]/following-sibling::div/*/strong/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = (
            loc_dom.xpath("//iframe/@src")[0]
            .split("!2d")[-1]
            .split("!2m")[0]
            .split("!3d")
        )
        latitude = geo[1]
        longitude = geo[0]
        hoo = loc_dom.xpath(
            '//h5[contains(text(), "REGULAR STAFFED HOURS")]/following-sibling::div/*/text()'
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
