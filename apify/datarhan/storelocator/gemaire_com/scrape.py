import csv
import json

from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


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

    DOMAIN = "gemaire.com"
    start_url = "https://www.gemaire.com/branch/service/locate/?address={}"

    all_locations = []
    all_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=200,
        max_search_results=None,
    )
    for code in all_codes:
        response = session.get(start_url.format(code))
        data = json.loads(response.text)
        if data.get("branches"):
            all_locations += data["branches"]

    for poi in all_locations:
        if type(poi) == str:
            continue
        store_url = "<MISSING>"
        location_name = poi["branch_name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["address_2"]
        if poi["address"]["address_3"]:
            street_address += ", " + poi["address"]["address_3"]
        city = poi["address"]["city"]
        state = poi["address"]["state"]
        zip_code = poi["address"]["postcode"]
        country_code = poi["address"]["country"]
        store_number = poi["branch_id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        days = {
            "1": "Monday",
            "2": "Tuesday",
            "3": "Wendsday",
            "4": "Thursday",
            "5": "Friday",
            "6": "Satarday",
            "7": "Sunday",
        }
        for day, hours in poi["formatted_hours"].items():
            day = days[day]
            if hours["isOpen"]:
                opens = hours["open"]
                closes = hours["close"]
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
