import re
import csv
import demjson
from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
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

    start_url = "http://www.eggsmart.com/locations.aspx"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    all_locations = []
    all_codes = DynamicZipSearch(country_codes=[SearchableCountries.CANADA])
    for code in all_codes:
        formdata = {"city": "Ajax", "address": code}
        response = session.post(start_url, data=formdata)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//a[contains(text(), "Store Details")]/@href')
        pages = dom.xpath('//nav[@class="pagination"]//a/@href')
        for url in pages:
            if "java" in url:
                continue
            response = session.get(urljoin(start_url, url))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath('//a[contains(text(), "Store Details")]/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="location-detail"]/h2/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_address = " ".join(
            loc_dom.xpath('//div[@class="location-detail"]/p/text()')[0].split()
        )
        addr = parse_address_intl(raw_address)
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
        store_number = location_name.split()[-1]
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')[0].split()[-1]
        location_type = "<MISSING>"
        data = loc_dom.xpath('//script[contains(text(),  "locations")]/text()')[1]
        data = re.findall(
            "locations = (.+);.+var map",
            data.replace("\n", "").replace("eval(", "").replace("),", ","),
        )[0]
        data = demjson.decode(data)
        poi = [e for e in data if e["address"].replace("&apos;", "'") in raw_address][0]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = loc_dom.xpath('//div[@class="hours"]//text()')
        hoo = [" ".join([s.strip() for s in e.split()]) for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo[1:]) if hoo else "<MISSING>"

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
