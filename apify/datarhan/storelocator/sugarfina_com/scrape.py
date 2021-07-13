import math
import csv
from lxml import etree

from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries
from concurrent.futures import ThreadPoolExecutor, as_completed


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


session = SgRequests()


def fetch(page, postal):
    start_url = "https://www.sugarfina.com/rest/V1/storelocator/search/"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }

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
        "searchCriteria[filter_groups][0][filters][5][value]": postal,
        "searchCriteria[filter_groups][0][filters][5][condition_type]": "eq",
        "searchCriteria[filter_groups][0][filters][6][field]": "distance",
        "searchCriteria[filter_groups][0][filters][6][value]": "20000",
        "searchCriteria[filter_groups][0][filters][6][condition_type]": "eq",
        "searchCriteria[filter_groups][0][filters][7][field]": "onlyLocation",
        "searchCriteria[filter_groups][0][filters][7][value]": "0",
        "searchCriteria[filter_groups][0][filters][7][condition_type]": "eq",
        "searchCriteria[filter_groups][0][filters][8][field]": "store_type",
        "searchCriteria[filter_groups][0][filters][8][value]": "",
        "searchCriteria[filter_groups][0][filters][8][condition_type]": "eq",
        "searchCriteria[current_page]": page,
        "searchCriteria[page_size]": "9",
    }

    return session.get(start_url, headers=hdr, params=params).json()


def fetch_locations(postal, locations, tracker, executor):
    total = fetch(0, postal)["total_count"]
    pages = range(1, math.ceil(total / 9) + 2)

    futures = [executor.submit(fetch, page, postal) for page in pages]
    for future in as_completed(futures):
        result = future.result()
        for item in result["items"]:
            id = f'{item["name"]}-{item["street"]}-{item["postal_code"]}'
            if id not in tracker:
                tracker.append(id)
                locations.append(item)


def extract(poi):
    domain = "sugarfina.com"
    store_url = poi.get("store_details_link")
    if store_url:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
    else:
        loc_dom = "<MISSING>"

    store_url = store_url if store_url else "<MISSING>"
    location_name = poi["name"]
    location_name = location_name.strip() if location_name else "<MISSING>"
    street_address = poi["street"]
    street_address = street_address if street_address else "<MISSING>"
    city = poi["city"].strip()
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

    return [
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


def fetch_data():
    # Your scraper here
    locations = []
    tracker = []

    with ThreadPoolExecutor() as executor:
        search = static_zipcode_list(200, SearchableCountries.USA)
        for postal in search:
            fetch_locations(postal, locations, tracker, executor)

        futures = [executor.submit(extract, location) for location in locations]
        for future in as_completed(futures):
            yield future.result()


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
