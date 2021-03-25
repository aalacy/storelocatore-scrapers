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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    start_url = "https://aws.servicehub.eurostep.it/api/storelocators/coord/{}/{}"
    domain = "moleskine.com"

    all_coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=30
    )
    for lat, lng in all_coords:
        response = session.get(start_url.format(lng, lat))
        if "No stores found" in response.text:
            continue
        data = json.loads(response.text)

        for poi in data["storesList"]:
            store_url = "https://us.moleskine.com/en/store-locator"
            location_name = poi["store_name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["address"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["city"]
            city = city if city else "<MISSING>"
            state = poi["province"]
            state = state if state else "<MISSING>"
            zip_code = poi["zip_code"]
            zip_code = zip_code if zip_code else "<MISSING>"
            if state in zip_code:
                zip_code = "-".join(zip_code.split("-")[1:])
            country_code = poi["country"]
            country_code = country_code if country_code else "<MISSING>"
            if country_code != "United States":
                continue
            store_number = poi["id"]
            phone = poi["phone"]
            phone = phone if phone else "<MISSING>"
            location_type = str(poi["type_of_shop"])
            if location_type == "1":
                location_type = "Moleskin Store"
            elif location_type == "3":
                location_type = "Retailer"
            latitude = poi["location"]["coordinates"][-1]
            longitude = poi["location"]["coordinates"][0]
            hours_of_operation = "<MISSING>"

            item = [
                domain,
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
