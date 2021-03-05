import csv
import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


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

    DOMAIN = "chanel.com"
    start_url = "https://services.chanel.com/en_GB/storelocator/getStoreList"

    headers = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=10,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        radius = 60.7
        lat_min = float(lat) - (0.009 * radius)
        lat_max = float(lat) + (0.009 * radius)
        lng_min = float(lng) - (0.009 * radius)
        lng_max = float(lng) + (0.009 * radius)
        lat_min = str(lat_min)
        lat_max = str(lat_max)
        lng_min = str(lng_min)
        lng_max = str(lng_max)

        formdata = {
            str("division[]"): "1",
            str("productline[]"): "1",
            str("productline[]"): "2",
            str("productline[]"): "3",
            str("productline[]"): "4",
            str("division[]"): "2",
            str("productline[]"): "5",
            str("productline[]"): "6",
            str("division[]"): "5",
            str("productline[]"): "18",
            str("productline[]"): "19",
            str("productline[]"): "25",
            str("division[]"): "3",
            str("productline[]"): "10",
            str("productline[]"): "14",
            str("productline[]"): "13",
            str("productline[]"): "12",
            "chanel-only": "1",
            "geocodeResults": '[{"address_components":[],"formatted_address":"","geometry":{"bounds":{"south":%s,"west":%s,"north":%s,"east":%s},"location":{"lat":%s,"lng":%s},"location_type":"GEOMETRIC_CENTER","viewport":{"south":%s,"west":%s,"north":%s,"east":%s}},"place_id":"","types":["route"]}]'
            % (
                lat_min,
                lng_min,
                lat_max,
                lng_max,
                lat,
                lng,
                lat_min,
                lng_min,
                lat_max,
                lng_max,
            ),
            "radius": "60.7",
        }
        response = session.post(start_url, data=formdata, headers=headers)
        data = json.loads(response.text)
        all_locations += data["stores"]

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = poi["translations"][0]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["translations"][0]["address1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["translations"][0]["cityname"]
        city = city if city else "<MISSING>"
        state = poi["statename"]
        state = state if state else "<MISSING>"
        zip_code = poi["zipcode"]
        country_code = "<MISSING>"
        if poi["countryid"] == "77":
            country_code = "UK"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["translations"][0]["division_name"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"
        if poi["openinghours"]:
            day = poi["openinghours"][0]["day"]
            hours = poi["openinghours"][0]["opening"]
            hours_of_operation = f"{day} {hours}"

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
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
