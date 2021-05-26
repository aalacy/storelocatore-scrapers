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

    start_url = "https://www2.super-saver.com/StoreLocator/Store_MapDistance_S.las?miles=50000&zipcode=51501"
    domain = "super-saver.com"
    hdr = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    all_locations = json.loads(response.text)

    for poi in all_locations:
        store_url = f'https://www2.super-saver.com/StoreLocator/Store?L={poi["StoreNbr"]}&M=&From=&S='
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = "<MISSING>"
        raw_address = loc_dom.xpath('//p[@class="Address"]/text()')
        raw_address = [
            " ".join([s.strip() for s in e.strip().split()])
            for e in raw_address
            if e.strip()
        ]
        street_address = raw_address[0].strip()
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = poi["StoreNbr"]
        phone = loc_dom.xpath('//p[@class="PhoneNumber"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = re.findall(r"initializeMap\((.+?)\);", loc_response.text)[0][1:-1].split(
            ","
        )
        latitude = geo[0][:-1]
        longitude = geo[1][1:]
        hoo = loc_dom.xpath(
            '//dt[contains(text(), "Hours of Operation:")]/following-sibling::dd/text()'
        )
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
