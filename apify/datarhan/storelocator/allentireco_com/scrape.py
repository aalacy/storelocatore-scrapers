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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "allentireco.com"
    start_url = "https://www.allentireco.com/wp-json/monro/v1/stores/coords?latitude={}&longitude={}&distance=50"

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=50,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng))
        data = json.loads(response.text)
        all_locations += data["data"]

    for poi in all_locations:
        location_name = poi["BrandDisplayName"]
        street_address = poi["Address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["StateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["ZipCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["Id"]
        phone = poi["SalesPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        hoo_dict = {}
        for key, value in poi.items():
            if "OpenTime" in key:
                day = key.replace("OpenTime", "")
                opens = value
                if hoo_dict.get(day):
                    hoo_dict[day]["opens"] = opens
                else:
                    hoo_dict[day] = {}
                    hoo_dict[day]["opens"] = opens
            if "CloseTime" in key:
                day = key.replace("CloseTime", "")
                closes = value
                if hoo_dict.get(day):
                    hoo_dict[day]["closes"] = closes
                else:
                    hoo_dict[day] = {}
                    hoo_dict[day]["closes"] = closes

        for day, hours in hoo_dict.items():
            opens = hours["opens"]
            closes = hours["closes"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )
        store_url = "https://www.allentireco.com/store-search/"

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
