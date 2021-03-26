import re
import csv
import demjson
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

    start_url = "https://www.softmoc.com/ca/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "var locations")]/text()')[0]
    data = re.findall(r"var locations =(.+?\]);", data.replace("\n", ""))[-1]
    data = demjson.decode(data)

    for poi in data:
        store_url = start_url
        location_name = poi["details"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["details"]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["details"]["city"]
        city = city if city else "<MISSING>"
        state = poi["details"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["details"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["details"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["details"]["id"]
        phone = poi["details"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = "<MISSING>"

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
