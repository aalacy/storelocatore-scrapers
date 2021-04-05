import re
import csv
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
    session = SgRequests()

    items = []

    DOMAIN = "travelodge.co.uk"
    start_url = "https://www.travelodge.co.uk/search_and_book/a-to-z/"

    all_locations = []
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_cities = dom.xpath('//a[@class="espotLink"]/@href')

    for url in all_cities:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(@href, "/hotels/")]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        all_locations += dom.xpath('//a[span[contains(text(), "View hotel")]]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        all_locations += dom.xpath('//a[span[contains(text(), "View hotel")]]/@href')

        location_name = loc_dom.xpath('//h1[@property="schema:name"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = loc_dom.xpath('//div[@property="schema:address"]/text()')
        raw_address = [
            " ".join([e.strip() for e in elem.strip().split()])
            for elem in raw_address
            if elem.strip()
        ]
        if not raw_address:
            continue
        if "United Kingdom" in raw_address[0]:
            raw_address = [raw_address[0].split(", ")[0]] + [
                ", ".join(raw_address[0].split(", ")[1:])
            ]
        if "Madrid" in raw_address[0]:
            raw_address = [raw_address[0].split("Madrid")[0]] + [
                "Madrid, " + " ".join(raw_address[0].split(", ")[1:])
            ]
        street_address = raw_address[0].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = raw_address[1].split(", ")[0]
        state = "<MISSING>"
        if len(raw_address[1].split(", ")) == 4:
            zip_code = raw_address[1].split(", ")[2]
        else:
            zip_code = raw_address[1].split(", ")[1]
        country_code = raw_address[1].split(", ")[-1]
        store_number = loc_response.url.split("/")[-2]
        phone = loc_dom.xpath('//a[@class="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall("hotelLat: '(.+?)',", loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall("hotelLng: '(.+?)',", loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

        if "United Kingdom" in zip_code:
            zip_code = city
            city = street_address.split(", ")[-1]
            street_address = ", ".join(street_address.split(", ")[:-1])
        if city == "Spain":
            city = street_address.split(", ")[-1]
            street_address = ", ".join(street_address.split(", ")[:-1])
        if not street_address:
            street_address = city
            city = "London"
        if "Use" in zip_code:
            zip_code = zip_code.split("Use")[0].strip()
        if "Spain" in zip_code:
            zip_code = zip_code.split()[-2]
            country_code = country_code.split()[-1]

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
