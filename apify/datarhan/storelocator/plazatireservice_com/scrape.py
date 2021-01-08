import csv
import json

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests


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

    items = []
    scraped_items = []

    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    DOMAIN = "plazatireservice.com"
    start_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=100&location={}&limit=50&api_key=d63dc113abd21389a57501752594b46a&v=20181201&resolvePlaceholders=true&savedFilterIds=143521617"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=100,
        max_search_results=None,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        all_locations += data["response"]["entities"]

    for poi in all_locations:
        store_url = poi["landingPageUrl"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code.strip() if zip_code else "<MISSING>"
        country_code = poi["address"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["meta"]["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["mainPhone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi.get("displayCoordinate"):
            latitude = poi["displayCoordinate"]["latitude"]
            longitude = poi["displayCoordinate"]["longitude"]
        if poi.get("yextDisplayCoordinate"):
            latitude = poi["yextDisplayCoordinate"]["latitude"]
            longitude = poi["yextDisplayCoordinate"]["longitude"]
        hours_of_operation = []
        for day, hours in poi["hours"].items():
            if day == "holidayHours":
                continue
            if hours.get("isClosed"):
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
