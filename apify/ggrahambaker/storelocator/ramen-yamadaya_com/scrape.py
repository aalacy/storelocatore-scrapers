import re
import csv
import json
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

    start_url = "https://www.ramen-yamadaya.com/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//nav[@class="index-navigation collection-nav"]//a/@href'
    )
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath("//@data-block-json")[-1]
        poi = json.loads(poi)

        location_name = poi["location"]["addressTitle"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["location"]["addressLine1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["location"]["addressLine2"].split(", ")[0]
        state = poi["location"]["addressLine2"].split(", ")[1]
        zip_code = poi["location"]["addressLine2"].split(", ")[-1]
        country_code = poi["location"]["addressCountry"]
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//p[contains(text(), "PHONE")]/text()')[-1]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["mapLat"]
        longitude = poi["location"]["mapLng"]
        hoo = loc_dom.xpath(
            '//h3[contains(text(), "HOURS")]/following-sibling::p[1]//text()'
        )
        if not hoo:
            hoo = loc_dom.xpath('//p[contains(text(), "HOURS")]//text()')[1:]
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
