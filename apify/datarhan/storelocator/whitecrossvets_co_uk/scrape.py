import re
import csv
import json
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

    DOMAIN = "whitecrossvets.co.uk"

    start_url = "https://www.whitecrossvets.co.uk/branch-finder/"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "practicesData")]/text()')[0]
    data = re.findall("practicesData =(.+);", data)[0]
    data = json.loads(data)

    for poi in data["practices"]:
        store_url = poi["guid"]
        location_name = poi["post_title"]
        location_name = location_name if location_name else "<MISSING>"
        raw_address = poi["address"].split(", ")
        raw_address = (
            " ".join([elem.strip() for elem in raw_address])
            .split("Please")[0]
            .replace("(For Sat Nav use: SK14 4EQ)", "")
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_1
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        store_number = poi["ID"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        country_code = "UK"
        location_type = poi["post_type"]
        geo = poi["location"].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hoo = etree.HTML(poi["opening_hours"])
        hoo = [elem.strip() for elem in hoo.xpath("//text()") if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
