import csv
import json

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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []
    scraped_items = []

    DOMAIN = "jlindeberg.com"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    countries = ["US", "CA", "GB"]
    for country_code in countries:
        url = "https://www.jlindeberg.com/on/demandware.store/Sites-BSE-South-Site/en_GB/Stores-GetCities?countryCode={}&brandCode=jl".format(
            country_code
        )
        response = session.get(url, headers=headers)
        data = json.loads(response.text)
        for city in data:
            final_url = "https://www.jlindeberg.com/on/demandware.store/Sites-BSE-South-Site/en_GB/PickupLocation-GetLocations?countryCode={}&brandCode=jl&postalCodeCity={}&serviceID=SDSStores&filterByClickNCollect=false"
            final_url = final_url.format(country_code, city)
            city_response = session.get(final_url, headers=headers)
            locations = json.loads(city_response.text)

            for poi in locations["locations"]:
                store_url = "https://www.jlindeberg.com/gb/en/stores"
                location_name = poi["storeName"]
                street_address = poi["address1"]
                street_address = street_address if street_address else "<MISSING>"
                state = poi.get("state")
                state = state if state else "<MISSING>"
                zip_code = poi["postalCode"]
                zip_code = zip_code if zip_code else "<MISSING>"
                store_number = poi["storeID"]
                phone = poi["phone"]
                phone = phone if phone else "<MISSING>"
                location_type = "<MISSING>"
                latitude = poi["latitude"]
                latitude = latitude if latitude else "<MISSING>"
                longitude = poi["longitude"]
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
