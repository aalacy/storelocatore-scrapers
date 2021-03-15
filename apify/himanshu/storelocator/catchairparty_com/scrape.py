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

    start_url = "https://catchairparty.com/locations/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="location_btm"]')
    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h4/a/@href")[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        raw_address = poi_html.xpath(".//p/text()")[0]
        addr = parse_address_intl(raw_address)

        location_name = poi_html.xpath(".//a/text()")
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        if "Currently Closed" in street_address:
            continue
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
            '//div[@class="col-lg-4 col-md-4 col-sm-6 col-xs-12"]/div/a/text()'
        )
        if not phone:
            phone = poi_html.xpath(".//p/text()")[1].split("|")[0].strip()
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hoo = loc_dom.xpath(
            '//h2[contains(text(), "STORE HOURS")]/following-sibling::p/text()'
        )
        if not hoo:
            hoo = loc_dom.xpath('//div[h2[contains(text(), "STORE HOURS")]]/text()')
        if hoo:
            hoo = [e.strip() for e in hoo[1:] if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        if "Paramus" in city:
            phone = "201-620-2125"

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
