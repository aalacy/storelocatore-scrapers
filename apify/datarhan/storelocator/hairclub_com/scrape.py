import re
import csv
from lxml import etree
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "hairclub.com"
    start_url = "https://www.hairclub.com/find-a-center/?zipcode={}&search_string={}"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_radius_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        response = session.get(start_url.format(code, code))
        dom = etree.HTML(response.text)

        all_locations = dom.xpath('//li[@class="centers-list-item"]')
        for poi_html in all_locations:
            store_url = (
                "https://www.hairclub.com" + poi_html.xpath(".//header/a/@href")[0]
            )
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)

            location_name = poi_html.xpath(".//header/a/text()")
            location_name = location_name[0] if location_name else "<MISSING>"
            address_raw = store_dom.xpath(
                '//ul[@class="center-info-address-list center-info-list list-unstyled"]/li/text()'
            )
            street_address = address_raw[1]
            street_address = street_address if street_address else "<MISSING>"
            city = address_raw[2].split(",")[0]
            city = city if city else "<MISSING>"
            state = address_raw[2].split(",")[-1].split()[0]
            state = state if state else "<MISSING>"
            zip_code = address_raw[2].split(",")[-1].split()[-1]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = re.findall("\d+", address_raw[0])
            store_number = store_number[0] if store_number else "<MISSING>"
            phone = store_dom.xpath("//@data-js-web-phone")
            phone = phone[0].strip() if phone else ""
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = store_dom.xpath("//@data-js-lat")
            latitude = latitude[0] if latitude else "<MISSING>"
            longitude = store_dom.xpath("//@data-js-lon")
            longitude = longitude[0] if longitude else "<MISSING>"
            hours_of_operation = store_dom.xpath(
                '//ul[@class="center-info-hours-list center-info-list list-unstyled"]//text()'
            )
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if elem.strip()
            ]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )

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
