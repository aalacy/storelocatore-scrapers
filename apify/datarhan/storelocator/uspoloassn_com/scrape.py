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

    DOMAIN = "uspoloassn.com"
    start_url = "https://uspoloassnglobal.com/stores/location/{},{}/radius/200/lang/en/storeType/"

    all_locations = []
    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    for lat, lng in all_coordinates:
        response = session.get(start_url.format(lat, lng))
        data = json.loads(response.text)
        if data["response"]:
            all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        if country_code != "US":
            continue
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["meta"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["meta"]["schemaTypes"][0]
        if "Event" in location_type:
            continue
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["displayCoordinate"]:
            latitude = poi["displayCoordinate"]["latitude"]
            longitude = poi["displayCoordinate"]["longitude"]
        hoo = []
        if poi["hours"]:
            for day, hours in poi["hours"].items():
                if hours["isClosed"]:
                    hoo.append(f"{day} closed")
                else:
                    opens = hours["openIntervals"][0]["start"]
                    closes = hours["openIntervals"][0]["end"]
                    hoo.append(f"{day} {opens} - {closes}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
