import re
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

    DOMAIN = "associatedbank.com"
    start_url = "https://locatorapi.moneypass.com/Service.svc/locations/atm?format=json&callback=MoneyPassServiceCallback&spatialFilter=nearby({},{},%2040%20)&start=0&count=100&key=SFoS4aJaTztUVy3"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=50,
        max_search_results=None,
    )
    for lat, lng in search:

        response = session.get(start_url.format(lat, lng))
        data = re.findall(r"MoneyPassServiceCallback\((.+)\);", response.text)[0]
        data = json.loads(data)

        for poi in data["results"]:
            store_url = "<MISSING>"
            location_name = poi["atmLocation"]["name"]
            location_name = location_name if location_name else "<MISSING>"
            street_address = poi["atmLocation"]["address"]["street"]
            street_address = street_address if street_address else "<MISSING>"
            city = poi["atmLocation"]["address"]["city"]
            city = city if city else "<MISSING>"
            state = poi["atmLocation"]["address"]["state"]
            state = state if state else "<MISSING>"
            zip_code = poi["atmLocation"]["address"]["postalCode"]
            zip_code = zip_code if zip_code else "<MISSING>"
            country_code = poi["atmLocation"]["address"]["country"]
            country_code = country_code if country_code else "<MISSING>"
            store_number = poi["atmLocation"]["id"]
            store_number = store_number if store_number else "<MISSING>"
            phone = "<MISSING>"
            location_type = "<MISSING>"
            latitude = poi["atmLocation"]["coordinates"]["latitude"]
            latitude = latitude if latitude else "<MISSING>"
            longitude = poi["atmLocation"]["coordinates"]["longitude"]
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
            check = "{} {}".format(street_address, location_name)
            if check not in scraped_items:
                scraped_items.append(check)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
