import re
import csv

from bs4 import BeautifulSoup

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
    session = SgRequests()

    items = []

    domain = "https://www.prezzorestaurants.co.uk/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(domain, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_locations = base.find(id="visit-restaurant").find_all("option")[1:]

    for url in all_locations:
        store_url = domain + url["value"].split("?")[0]
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath(
            '//h2[@class="title mb-2 has-text-weight-bold"]/text()'
        )
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        raw_address = loc_dom.xpath(
            '//h4[a[contains(@href, "tel")]]/following-sibling::div[1]/p[1]/text()'
        )
        raw_address = [" ".join(e.split()) for e in raw_address][0]
        addr = parse_address_intl(raw_address)
        street_address = ", ".join(raw_address.split(", ")[:-2])
        city = addr.city
        city = city if city else "<MISSING>"
        if city in street_address:
            street_address = street_address.split(f", {city}")[0]
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "/@" in loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]:
            geo = (
                loc_dom.xpath('//a[contains(@href, "maps")]/@href')[0]
                .split("/@")[-1]
                .split(",")[:2]
            )
            latitude = geo[0]
            longitude = geo[1]

        loc_response = session.get(store_url + "?X-Requested-With=XMLHttpRequest")
        hoo = loc_dom.xpath(
            '//div[h4[contains(text(), "Opening times")]]/following-sibling::div//text()'
        )
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
