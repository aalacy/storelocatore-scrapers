import re
import csv
import json
from lxml import etree
from w3lib.html import remove_tags

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

    DOMAIN = "specsonline.com"
    start_url = "https://specsonline.com/locations/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath(
        '//div[@class="instore-store "]//a[contains(text(), "location detail")]/@href'
    )
    all_locations += dom.xpath(
        '//div[@class="instore-store hidden-stores"]//a[contains(text(), "location detail")]/@href'
    )

    data = dom.xpath('//script[@id="maplistko-js-extra"]/text()')[0]
    data = re.findall("ParamsKo =(.+);", data)[0]
    data = json.loads(data)

    for poi in data["KOObject"][0]["locations"]:
        store_url = poi["locationUrl"]
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        address_raw = etree.HTML(poi["address"])
        address_raw = address_raw.xpath(".//text()")
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        if len(address_raw) == 3:
            address_raw = [", ".join(address_raw[:2])] + address_raw[2:]
        street_address = address_raw[0]
        city = address_raw[1].split(",")[0]
        state = address_raw[1].split(",")[-1].split()[0]
        if state.isdigit():
            state = "<MISSING>"
        zip_code = address_raw[1].split(",")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = ""
        if poi.get("simpledescription"):
            phone = remove_tags(poi["simpledescription"]).split()[0]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        hours_of_operation = loc_dom.xpath('//p[@class="maplist-hours"]/text()')
        hours_of_operation = (
            hours_of_operation[0].strip() if hours_of_operation else "<MISSING>"
        )
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

        if phone == "<MISSING>":
            phone = loc_dom.xpath('//span[@itemprop="telephone"]/text()')
            phone = phone[0] if phone else "<MISSING>"

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
