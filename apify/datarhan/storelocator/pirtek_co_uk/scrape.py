import re
import csv
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "pirtek.co.uk"
    start_url = "https://www.pirtek.co.uk/service-centres"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//select[@class="selectric jump smaller"]/option/@value')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        if store_url == "https://www.pirtek.co.uk/service-centres":
            continue
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//h1[@class="serviceCentresTitle"]//span/text()')
        location_name = [elem.strip() for elem in location_name if elem.strip()]
        location_name = " ".join(location_name) if location_name else "<MISSING>"
        raw_address = " ".join(
            loc_dom.xpath(
                '//p[strong[contains(text(), "Contact Details")]]/following-sibling::p[1]/text()'
            )
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_1
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = " ".join(raw_address.split()[-2:])
        zip_code = zip_code if zip_code else "<MISSING>"
        phone = loc_dom.xpath('//p[contains(text(), "Tel:")]/text()')
        phone = phone[0].split(": ")[-1] if phone else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        if country_code == "Ireland":
            continue
        store_number = loc_response.url.split("/")[-2]
        location_type = "<MISSING>"
        geo = re.findall(r"LatLng\((.+?)\),", loc_response.text)
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if geo:
            geo = geo[0].split(", ")
            latitude = geo[0]
            longitude = geo[1]
        hours_of_operation = "<MISSING>"

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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
