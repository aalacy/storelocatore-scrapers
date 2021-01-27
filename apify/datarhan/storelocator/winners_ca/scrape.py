import json
import csv

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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "winners.ca"
    start_url = "https://marketingsl.tjx.com/storelocator/GetSearchResults"

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=100,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        formdata = {
            "chain": "91",
            "geolat": lat,
            "geolong": lng,
            "lang": "en",
            "maxstores": "250",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = session.post(start_url, headers=headers, data=formdata)
        data = json.loads(response.text)
        all_locations += data["Stores"]

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = "Winners at " + poi["Address2"]
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        state = poi["State"]
        zip_code = poi["Zip"]
        country_code = poi["Country"]
        store_number = poi["StoreID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["Hours"]
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
