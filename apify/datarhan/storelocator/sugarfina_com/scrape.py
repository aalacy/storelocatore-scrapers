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

    start_url = "https://www.sugarfina.com/rest/V1/storelocator/search/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=200
    )
    for code in all_codes:
        params = {
            "searchCriteria[filter_groups][0][filters][0][field]": "lat",
            "searchCriteria[filter_groups][0][filters][0][value]": "",
            "searchCriteria[filter_groups][0][filters][0][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][1][field]": "lng",
            "searchCriteria[filter_groups][0][filters][1][value]": "",
            "searchCriteria[filter_groups][0][filters][1][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][2][field]": "country_id",
            "searchCriteria[filter_groups][0][filters][2][value]": "US",
            "searchCriteria[filter_groups][0][filters][2][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][3][field]": "store_id",
            "searchCriteria[filter_groups][0][filters][3][value]": "1",
            "searchCriteria[filter_groups][0][filters][3][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][4][field]": "region_id",
            "searchCriteria[filter_groups][0][filters][4][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][5][field]": "region",
            "searchCriteria[filter_groups][0][filters][5][value]": code,
            "searchCriteria[filter_groups][0][filters][5][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][6][field]": "distance",
            "searchCriteria[filter_groups][0][filters][6][value]": "100",
            "searchCriteria[filter_groups][0][filters][6][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][7][field]": "onlyLocation",
            "searchCriteria[filter_groups][0][filters][7][value]": "0",
            "searchCriteria[filter_groups][0][filters][7][condition_type]": "eq",
            "searchCriteria[filter_groups][0][filters][8][field]": "store_type",
            "searchCriteria[filter_groups][0][filters][8][value]": "",
            "searchCriteria[filter_groups][0][filters][8][condition_type]": "eq",
            "searchCriteria[current_page]": "1",
            "searchCriteria[page_size]": "9",
        }
        response = session.get(start_url, headers=hdr, params=params)
        data = json.loads(response.text)
        all_locations += data["items"]

    for poi in all_locations:
        store_url = poi.get("store_details_link")
        if store_url:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name.strip() if location_name else "<MISSING>"
        street_address = poi["street"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi.get("region")
        state = state if state else "<MISSING>"
        zip_code = poi["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country_id"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi.get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = poi["store_type"]
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = []
        if store_url != "<MISSING>":
            hoo = loc_dom.xpath('//div[@class="store-timing"]/p//text()')
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
