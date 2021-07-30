import re
import csv
import json
from lxml import etree

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

    start_url = "https://www.dicanns.com/restaurants-1"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//div[contains(@data-block-json, "location")]/@data-block-json'
    )
    for poi in all_locations:
        poi = json.loads(poi)
        store_url = start_url
        location_name = poi["location"]["addressTitle"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["location"]["addressLine1"]
        if not street_address:
            continue
        raw_data = poi["location"]["addressLine2"].split(", ")
        city = raw_data[0]
        state = raw_data[1]
        zip_code = raw_data[-1]
        country_code = poi["location"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = dom.xpath(
            '//div[div[contains(@data-block-json, "{}")]]/following-sibling::div//*[contains(text(), "Tel")]/text()'.format(
                location_name
            )
        )
        if not phone:
            phone = dom.xpath(
                '//div[contains(@data-block-json, "{}")]/following-sibling::div//*[contains(text(), "Tel")]/text()'.format(
                    location_name
                )
            )
        phone = phone[0].split(":")[-1].strip() if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["mapLat"]
        longitude = poi["location"]["mapLng"]
        hoo = dom.xpath(
            '//div[div[contains(@data-block-json, "{}")]]/preceding-sibling::div//p/text()'.format(
                location_name
            )
        )[4:]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo).split("HOURS ")[-1] if hoo else "<MISSING>"
        hours_of_operation = hours_of_operation.split("Hours ")[-1]

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
