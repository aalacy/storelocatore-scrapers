import csv
import json
from lxml import etree

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "imospizza.com"
    start_url = "https://www.imospizza.com/wp-admin/admin-ajax.php"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=100,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        formdata = {
            "action": "get_stores",
            "lat": lat,
            "lng": lng,
            "radius": "100",
            "categories[0]": "",
        }
        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)
        for poi in data.values():
            all_locations.append(poi)

    for poi in all_locations:
        poi_url = poi["gu"]
        poi_name = poi["na"]
        poi_name = poi_name if poi_name else "<MISSING>"
        street = poi["st"]
        street = street if street else "<MISSING>"
        city = poi["ct"]
        city = city if city else "<MISSING>"
        state = poi["rg"]
        state = state if state else "<MISSING>"
        zip_code = poi["zp"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        poi_number = poi["ID"]
        poi_number = poi_number if poi_number else "<MISSING>"
        phone = poi["te"]
        phone = phone if phone else "<MISSING>"
        poi_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]

        if poi_number in scraped_items:
            continue

        store_response = session.get(poi_url)
        store_dom = etree.HTML(store_response.text)
        hoo = store_dom.xpath('//div[@class="hours__store"]//text()')[1:]
        hoo = " ".join(hoo).replace("\n", "")

        item = [
            DOMAIN,
            poi_url,
            poi_name,
            street,
            city,
            state,
            zip_code,
            country_code,
            poi_number,
            phone,
            poi_type,
            latitude,
            longitude,
            hoo,
        ]
        if poi_number not in scraped_items:
            scraped_items.append(poi_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
