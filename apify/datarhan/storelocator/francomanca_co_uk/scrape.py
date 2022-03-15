import re
import csv
import json
from lxml import etree
from urllib.parse import urljoin

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

    DOMAIN = "francomanca.co.uk"
    start_url = "https://www.francomanca.co.uk/restaurants/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "siteData = ")]/text()')[0]
    data = re.findall("var siteData =(.+)", data)[0]
    data = json.loads(data)

    for poi in data:
        if not poi["location"]:
            continue
        store_url = urljoin(start_url, poi["name"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["title"]
        raw_address = poi["location"]["address"]
        address = parse_address_intl(raw_address)
        street_address = address.street_address_1
        street_address = street_address if street_address else "<MISSING>"
        if "Italy" in street_address:
            continue
        city = address.city
        city = city if city else "<MISSING>"
        state = address.state
        state = state if state else "<MISSING>"
        zip_code = address.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        latitude = poi["location"]["lat"]
        longitude = poi["location"]["lng"]
        country_code = poi["location"].get("country_short")
        if not country_code:
            country_code = address.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["ID"]
        phone = loc_dom.xpath('//a[@class="tel"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="opening_hours"]/text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
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
