import csv
import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    DOMAIN = "orangejulius.com"
    session = SgRequests()

    items = []
    scraped_items = []

    start_url = "https://prod-orangejulius-dairyqueen.dotcmscloud.com/api/vtl/locations?country=us&lat={}&long={}"

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=200
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng))
        data = json.loads(response.text)
        all_locations += data["locations"]

    for poi in all_locations:
        store_url = "https://www.dairyqueen.com/en-us" + poi["url"]
        location_name = poi["title"]
        location_name = (
            location_name.split(":")[-1].strip() if location_name else "<MISSING>"
        )
        street_address = poi["address3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["stateProvince"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["storeNo"]
        phone = "<MISSING>"
        location_type = poi["conceptType"]
        if poi["tempClosed"] or poi["comingSoon"]:
            continue
        latitude = poi["latlong"].split(",")[0]
        longitude = poi["latlong"].split(",")[1]
        longitude = longitude if longitude else "<MISSING>"
        hoo = poi.get("storeHours")
        hours_of_operation = hoo if hoo else "<MISSING>"

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
