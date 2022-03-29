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

    start_url = "https://palmbeachtan.com/locations/srj/{}/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=50
    )
    for code in all_codes:
        response = session.get(start_url.format(code), headers=hdr)
        if "/html" in response.text:
            continue
        all_locations += json.loads(response.text)

    for poi in all_locations:
        store_url = f'https://palmbeachtan.com/locations/{poi["salon_state"]}/{poi["salon_url"]}'
        if store_url in scraped_items:
            continue
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = poi["salon_name"]
        location_name = (
            location_name.replace(" - NOW HIRING!", "")
            if location_name
            else "<MISSING>"
        )
        street_address = poi["salon_address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["salon_city"]
        city = city if city else "<MISSING>"
        state = poi["salon_state"]
        state = state if state else "<MISSING>"
        zip_code = poi["salon_zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "US"
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = loc_dom.xpath('//data[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")[0]
        longitude = loc_dom.xpath("//@data-lng")[0]
        hoo = hoo = loc_dom.xpath('//aside[@class="hours"]//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = (
            " ".join(hoo[1:]).replace("Careers»", "").strip() if hoo else "<MISSING>"
        )

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
        if store_url not in scraped_items:
            scraped_items.append(store_url)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
