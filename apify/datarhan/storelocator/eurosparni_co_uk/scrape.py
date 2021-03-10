import re
import csv
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgpostal import parse_address_intl


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "eurosparni.co.uk"
    start_url = "https://www.eurosparni.co.uk/nearest-store?postcode={}"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN], max_radius_miles=50
    )
    for code in all_codes:
        store_url = start_url.format(code + "%201D0")
        response = session.get(store_url)
        dom = etree.HTML(response.text)
        all_locations = dom.xpath(
            '//div[@class="owl-item" and div[@class="large-7 large-offset-1 columns"]]'
        )

        for i, poi_html in enumerate(all_locations):
            store_url = "https://www.eurosparni.co.uk/nearest-store"
            location_name = poi_html.xpath('.//h1[@id="storeName"]/text()')
            if not location_name:
                continue
            location_name = location_name[0]
            raw_address = poi_html.xpath(
                './/h1[@id="storeName"]/following-sibling::p//text()'
            )
            raw_address = " ".join([e.strip() for e in raw_address if e.strip()])
            addr = parse_address_intl(raw_address)
            street_address = raw_address.split(",")[0]
            city = addr.city
            city = city if city else "<MISSING>"
            state = "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath('.//a[contains(@href, "tel")]/@href')
            phone = phone[0].split(":")[-1] if phone else "<MISSING>"
            location_type = "<MISSING>"
            geo = re.findall(r"location\d = (.+?);", response.text)[i]
            geo = demjson.decode(geo)
            latitude = geo["lat"]
            longitude = geo["lng"]
            hoo = poi_html.xpath(
                './/h5[contains(text(), "Opening Hours")]/following-sibling::table//text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()][3:]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

            if zip_code == "2h L":
                zip_code = "BT22 2hL"

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
