import re
import csv
import json
from lxml import etree

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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "dreamdoors.co.uk"
    start_url = "https://www.dreamdoors.co.uk/kitchen-showrooms"

    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=10,
        max_search_results=None,
    )
    for code in all_codes:
        formdata = {
            "option": "com_ajax",
            "module": "dreamdoors_store_finder",
            "postcode": code + " 0RS",
            "format": "raw",
        }
        headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        response = session.post(start_url, data=formdata, headers=headers)
        if response.status_code != 200:
            continue
        data = json.loads(response.text)

        for poi in data:
            if type(poi) == str:
                continue
            store_url = poi["url"]
            if store_url in scraped_items:
                continue
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
            location_name = poi["name"]
            location_name = location_name if location_name else "<MISSING>"
            raw_address = loc_dom.xpath('//div[@class="address"]/text()')
            raw_address = [elem.strip() for elem in raw_address if elem.strip()]
            addr = parse_address_intl(" ".join(raw_address))
            if addr.street_address_2:
                street_address = f"{addr.street_address_2} {addr.street_address_1}"
            else:
                street_address = addr.street_address_1
            city = addr.city
            city = city if city else "<MISSING>"
            state = "<MISSING>"
            zip_code = addr.postcode
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = addr.country
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["id"]
            store_number = store_number if store_number else "<MISSING>"
            phone = loc_dom.xpath('//a[@id="showroom-phone"]/text()')
            phone = phone[0] if phone else "<MISSING>"
            location_type = "<MISSING>"
            geo = re.findall(
                r'.map_initialize\("map_canvas", ".+", (.+?)\)', loc_response.text
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if geo:
                geo = geo[0].split(", ")
                latitude = geo[0]
                longitude = geo[1]
            hoo = loc_dom.xpath('//div[@class="opening_times"]//text()')
            hoo = [elem.strip() for elem in hoo if elem.strip()]
            hours_of_operation = (
                " ".join(hoo[2:]).split(" Call ")[0] if hoo else "<MISSING>"
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
            if store_url not in scraped_items:
                scraped_items.append(store_url)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
