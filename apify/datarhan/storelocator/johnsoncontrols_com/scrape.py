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
    scraped_stores = []

    DOMAIN = "johnsoncontrols.com"
    start_url = "https://jcilocationfinderapi-prod.azurewebsites.net/api/locationsapi/getnearbylocations?latitude={}&longitude={}&distance=none&units=mi&iso=en"

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6",
        "Connection": "keep-alive",
        "Host": "jcilocationfinderapi-prod.azurewebsites.net",
        "Origin": "https://www.johnsoncontrols.com",
        "Referer": "https://www.johnsoncontrols.com/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    }

    all_coordinates = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_radius_miles=50,
        max_search_results=None,
    )
    for coord in all_coordinates:
        lat, lng = coord
        response = session.get(start_url.format(lat, lng), headers=headers)
        data = json.loads(response.text)
        data = json.loads(data)

        for poi in data:
            store_url = ""
            store_url = store_url if store_url else "<MISSING>"
            location_name = poi["Name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["Address1"]
            if poi["Address2"]:
                street_address += ", " + poi["Address2"]
            if poi["Address3"]:
                street_address += poi["Address3"]
            if poi["Address4"]:
                street_address += poi["Address4"]
            street_address = (
                street_address.strip().replace(">", "")
                if street_address
                else "<MISSING>"
            )
            city = poi["City"]
            city = city if city else "<MISSING>"
            state = poi["State"]
            state = state.strip() if state else "<MISSING>"
            zip_code = poi["PostalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["Country"]
            if country_code not in ["USA", "United States", "Canada"]:
                continue
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["ID"]
            store_number = store_number if store_number else "<MISSING>"
            phone = ""
            if poi["PhoneNumbers"]["Phone"]:
                phone = poi["PhoneNumbers"]["Phone"][0]["Number"]
            phone = phone if phone else "<MISSING>"
            location_type = poi["LocationTypeName"]
            location_type = location_type if location_type else "<MISSING>"
            latitude = poi["Latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["Longitude"]
            longitude = longitude if longitude else "<MISSING>"
            hours_of_operation = ""
            hours_of_operation = (
                ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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

            check = "{} {}".format(location_name, street_address)
            if check not in scraped_stores:
                scraped_stores.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
