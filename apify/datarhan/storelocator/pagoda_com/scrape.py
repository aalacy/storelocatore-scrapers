import re
import csv
import demjson
import urllib.parse
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
    items = []

    DOMAIN = "pagoda.com"
    start_url = "https://www.pagoda.com/store-finder/view-all-states"
    scraped_locations = []

    session = SgRequests()
    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_states = dom.xpath(
        '//h1[contains(text(), "View All Stores")]/following-sibling::div[1]//a/@href'
    )
    for state_url in all_states:
        full_state_url = urllib.parse.urljoin(start_url, state_url)
        state_response = session.get(full_state_url)
        state_dom = etree.HTML(state_response.text)

        all_stores = state_dom.xpath(
            '//div[@class="inner-container storefinder-details view-all-stores"]/div/div[p[contains(text(), "Store List")]]'
        )
        for store_data in all_stores:
            store_url = store_data.xpath(".//a/@href")
            if store_url and "/store/null" not in store_url:
                store_url = urllib.parse.urljoin(start_url, store_url[0])
                store_name_fromlist = store_data.xpath(".//a/text()")
                location_type = "<MISSING>"
                store_response = session.get(store_url)
                store_dom = etree.HTML(store_response.text)
                data = store_dom.xpath(
                    '//script[contains(text(), "storeInformation")]/text()'
                )
                if not data:
                    continue
                data = re.findall(
                    "storeInformation = (.+);", data[0].replace("\n", "")
                )[0]
                data = demjson.decode(data)

                store_number = data["name"]
                location_name = store_dom.xpath('//h1[@itemprop="name"]/text()')
                if not location_name:
                    location_name = store_name_fromlist
                location_name = location_name[0] if location_name else "<MISSING>"
                street_address = store_data.xpath(
                    './/span[@itemprop="streetAddress"]/text()'
                )
                street_address = (
                    street_address[0].strip().replace("   ", " ")
                    if street_address
                    else "<MISSING>"
                )
                city = store_dom.xpath('//span[@itemprop="addressLocality"]/text()')
                city = city[0] if city else "<MISSING>"
                state = store_dom.xpath('//span[@itemprop="addressRegion"]/text()')
                state = state[0] if state else "<MISSING>"
                zip_code = store_dom.xpath('//span[@itemprop="postalCode"]/text()')
                zip_code = zip_code[0] if zip_code else "<MISSING>"
                phone = store_dom.xpath('//span[@itemprop="telephone"]/a/text()')
                phone = phone[0] if phone else "<MISSING>"
                country_code = store_dom.xpath(
                    '//span[@itemprop="addressCountry"]/text()'
                )
                country_code = country_code[0] if country_code else "<MISSING>"
                latitude = data["latitude"]
                latitude = latitude if latitude else "<MISSING>"
                longitude = data["longitude"]
                longitude = longitude if longitude else "<MISSING>"

                hoo = []
                for day, hours in data["openings"].items():
                    hoo.append(f"{day} {hours}")
                hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
            else:
                store_url = "<MISSING>"
                location_type = "<MISSING>"
                store_number = "<MISSING>"
                location_name = store_data.xpath(".//a/text()")
                location_name = location_name[0] if location_name else "<MISSING>"
                street_address = store_data.xpath(
                    './/span[@itemprop="streetAddress"]/text()'
                )
                street_address = street_address[0] if street_address else "<MISSING>"
                city = store_data.xpath('.//span[@itemprop="addressLocality"]/text()')
                city = city[0] if city else "<MISSING>"
                state = store_data.xpath('.//span[@itemprop="addressRegion"]/text()')
                state = state[0] if state else "<MISSING>"
                zip_code = store_data.xpath('.//span[@itemprop="postalCode"]/text()')
                zip_code = zip_code[0] if zip_code else "<MISSING>"
                phone = store_data.xpath('.//span[@itemprop="telephone"]/text()')
                phone = phone[0] if phone else "<MISSING>"
                country_code = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
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
            if check not in scraped_locations:
                scraped_locations.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
