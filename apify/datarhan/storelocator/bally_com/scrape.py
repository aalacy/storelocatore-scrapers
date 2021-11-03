import re
import csv
import json
from time import sleep
from lxml import etree

from sgrequests import SgRequests
from sgselenium import SgFirefox
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

    start_url = "https://www.bally.com/en/store-locator#address=United%20States&format=ajax&country=US"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    with SgFirefox() as driver:
        driver.get(start_url)
        sleep(10)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath("//div/@data-marker-info")
    for poi in all_locations:
        poi = json.loads(poi)
        store_url = poi["url"]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h2[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@class="js-store-address"]//text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        addr = parse_address_intl(" ".join(raw_address))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = loc_dom.xpath(
            '//span[@class="cs-option-text"]/a[contains(@href, "tel")]/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = loc_dom.xpath('//div[@class="store-hours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"

        # Exceptions
        if "Fl Aventura Fl" in street_address:
            street_address = street_address.split("Fl Aventura")[0]
            state = "FL"
            city = "Aventura"

        if "Fl Miami" in street_address:
            street_address = street_address.split("Fl Miami")[0]
            state = "FL"
            city = "Miami"

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
