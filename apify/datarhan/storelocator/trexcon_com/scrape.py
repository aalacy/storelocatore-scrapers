import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa


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

    start_url = "https://www.trexcon.com/all-locations"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//div[@class="image-button-inner"]/a/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath("//div/@data-block-json")[0]
        poi = json.loads(poi)

        location_name = loc_dom.xpath('//div[@class="sqs-block-content"]/h1/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        addr = parse_address_usa(
            poi["location"]["addressLine1"] + " " + poi["location"]["addressLine2"]
        )
        street_address = poi["location"]["addressLine1"]
        if not street_address:
            street_address = "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        if "#" in poi["location"]["addressTitle"]:
            store_number = poi["location"]["addressTitle"].split("#")[-1]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0].split(":")[-1] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["mapLat"]
        longitude = poi["location"]["mapLng"]
        hoo = loc_dom.xpath('//p[strong[contains(text(), "SUNDAY:")]]//text()')
        if not hoo:
            hoo = loc_dom.xpath('//p[strong[contains(text(), "HOURS")]]//text()')
        if not hoo:
            hoo = loc_dom.xpath('//p[strong[contains(text(), "TREX MART")]]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo).split("HOURS: ")[-1].replace("TREX MART ", "")
            if hoo
            else "<MISSING>"
        )
        if " SUBWAY HOURS " in hours_of_operation:
            hours_of_operation = hours_of_operation.split("HOURS ")[1].split(" SUBWAY")[
                0
            ]

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
