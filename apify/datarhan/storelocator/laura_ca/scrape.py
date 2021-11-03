import re
import csv
import json
from lxml import etree

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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
    scraped_items = []

    start_url = "https://www.laura.ca/en/stores-list/?dwfrm_storelocator_countryCode=CANADA&dwfrm_storelocator_distanceUnit=kilometers&dwfrm_storelocator_maxdistance=200&dwfrm_storelocator_lat=&dwfrm_storelocator_long=&dwfrm_storelocator_mapZoom=&dwfrm_storelocator_mapCenter=&dwfrm_storelocator_mapBounds=&dwfrm_storelocator_location={}&dwfrm_storelocator_storeType=&dwfrm_storelocator_findbyzip=Search"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA], max_radius_miles=100
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath("//tr[@data-store-details]")

    for poi_html in all_locations:
        poi = json.loads(poi_html.xpath("@data-store-details")[0])
        if poi["id"] in scraped_items:
            continue
        store_url = "https://www.laura.ca/en/store-details/?StoreID={}".format(
            poi["id"]
        )
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        raw_address = poi_html.xpath('.//div[@class="address-details"]/text()')
        raw_address = [e.strip() for e in raw_address if e.strip()]
        street_address = raw_address[0]
        city = raw_address[1].split(", ")[0]
        state = raw_address[1].split(", ")[-1].split()[0]
        zip_code = raw_address[1].split(", ")[-1].split()[-1]
        country_code = "CA"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = loc_dom.xpath(
            '//p[contains(text(), "Hours")]/following-sibling::table//text()'
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
