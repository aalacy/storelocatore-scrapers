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

    DOMAIN = "ccbg.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=200&location={}&limit=25&api_key=2d5a708a656b2665da2abeba0586c932&v=20181201&resolvePlaceholders=true&entityTypes=Location&savedFilterIds=20440614"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = poi["landingPageUrl"]
        location_name = poi["name"]
        if "Capital City Bank ATM" in location_name:
            continue
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["meta"]["id"]
        phone = poi["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = ", ".join(poi["services"])
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["geocodedCoordinate"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geocodedCoordinate"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if poi.get("hours"):
            for day, hours in poi["hours"].items():
                if hours.get("openIntervals"):
                    opens = hours["openIntervals"][0]["start"]
                    closes = hours["openIntervals"][0]["end"]
                    hours_of_operation.append(f"{day} {opens} - {closes}")
                else:
                    hours_of_operation.append(f"{day} closed")
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
