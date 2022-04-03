import csv
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

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

    DOMAIN = "dtlr.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=200&location=%22{}%22&limit=50&api_key=252cd5124c2d1f935854409f130acc61&v=20181201&resolvePlaceholders=true&entityTypes=location"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = poi.get("landingPageUrl")
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        if poi["address"].get("line2"):
            street_address += ", " + poi["address"]["line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["meta"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi.get("localPhone")
        phone = phone if phone else "<MISSING>"
        location_type = poi["meta"]["entityType"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi.get("geocodedCoordinate", {}).get("latitude")
        if not latitude:
            latitude = poi.get("yextDisplayCoordinate", {}).get("latitude")
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi.get("geocodedCoordinate", {}).get("longitude")
        if not longitude:
            longitude = poi.get("yextDisplayCoordinate", {}).get("longitude")
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if poi.get("hours"):
            for day, hours in poi["hours"].items():
                if day in ["reopenDate", "holidayHours"]:
                    continue
                if type(hours) == dict and hours.get("isClosed"):
                    hours_of_operation.append(f"{day} closed")
                else:
                    opens = hours["openIntervals"][0]["start"]
                    closes = hours["openIntervals"][0]["end"]
                    hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
        )

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
