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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "louisianafamousfriedchicken.net"
    start_url = "https://louisianafriedchickenhq.com/wp-admin/admin-ajax.php?action=store_search&lat={}&lng={}&max_results=100&search_radius=500&autoload=1"

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=500
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lat, lng))
        data = json.loads(response.text)

        for poi in data:
            store_url = poi["permalink"]
            location_type = "<MISSING>"
            hours_of_operation = poi["hours"]
            hours_of_operation = (
                hours_of_operation if hours_of_operation else "<MISSING>"
            )
            location_name = poi["store"]
            location_name = location_name if location_name else "<MISSING"
            street_address = poi["address"]
            city = poi["city"]
            state = poi["state"]
            zip_code = poi["zip"]
            if len(zip_code) > 5:
                zip_code = "<MISSING>"
            country_code = poi["country"]
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            latitude = poi["lat"]
            longitude = poi["lng"]

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
