import csv
import json
import sgzip
from sgzip import SearchableCountries

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

    DOMAIN = "hercrentals.com"

    all_codes = []
    us_zips = sgzip.for_radius(radius=50, country_code=SearchableCountries.USA)
    for zip_code in us_zips:
        all_codes.append(zip_code)

    start_url = "https://www.heb.com/commerce-api/v1/store/locator/address"
    headers = {
        "authority": "www.heb.com",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/json; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    for code in all_codes:
        body = '{"address":"%s","curbsideOnly":false,"radius":50}'
        response = session.post(start_url, headers=headers, data=body % code)
        data = json.loads(response.text)
        if not data.get("stores"):
            continue

        for poi in data["stores"]:
            location_name = poi["store"]["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["store"]["address1"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["store"]["city"]
            city = city if city else "<MISSING>"
            state = poi["store"]["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["store"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = ""
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["store"]["id"]
            store_number = store_number if store_number else "<MISSING>"
            phone = poi["store"]["phoneNumber"]
            phone = phone if phone else "<MISSING>"
            location_type = ""
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["store"]["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["store"]["longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = poi["store"]["storeHours"]

            store_url = "https://www.heb.com/heb-store/US/tx/san-antonio/south-flores-market-h-e-b-718"

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
