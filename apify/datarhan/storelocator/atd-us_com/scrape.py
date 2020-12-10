import csv
import json
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

    DOMAIN = "atd-us.com"
    start_url = "https://www.atd-us.com/atdcewebservices/v2/atdus/warehouse/search?latlong={},{}&distance=5000&lang=en&curr=USD"

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    headers = {
        "Host": "www.atd-us.com",
        "X-Anonymous-Consents": "%5B%5D",
        "Accept": "application/json, text/plain, */*",
        "Authorization": "bearer 382c0be2-0fc9-46ef-8422-fe15a5de471b",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    }

    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng), headers=headers)
        data = json.loads(response.text)

        for poi in data["warehouseList"]:
            store_url = "<MISSING>"
            location_name = poi["addressData"]["line1"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["addressData"]["line2"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["addressData"]["town"]
            city = city if city else "<MISSING>"
            state = poi["addressData"]["region"]["isocodeShort"]
            state = state if state else "<MISSING>"
            zip_code = poi["addressData"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = poi["dcCode"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["addressData"].get("phone")
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["addressData"]["latlong"].split(",")[0]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["addressData"]["latlong"].split(",")[-1]
            longitude = longitude if longitude else "<MISSING>"
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

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
