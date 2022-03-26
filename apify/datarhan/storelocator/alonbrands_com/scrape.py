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

    DOMAIN = "alonbrands.com"
    start_url = "https://alonbrands.com/wp-admin/admin-ajax.php"
    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=500
    )
    for lat, lng in all_coords:
        formdata = {
            "action": "get_stores",
            "lat": lat,
            "lng": lng,
            "radius": "500",
        }

        response = session.post(start_url, headers=hdr, data=formdata)
        data = json.loads(response.text)

        for n, poi in data.items():
            store_url = poi["gu"]
            store_url = store_url if store_url else "<MISSING>"
            location_name = poi["na"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["st"]
            city = poi["ct"]
            city = city if city else "<MISSING>"
            state = poi["rg"]
            state = state if state else "<MISSING>"
            zip_code = poi["zp"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = "<MISSING>"
            store_number = poi["ID"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["te"]
            phone = phone if phone else "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["lat"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["lng"]
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
