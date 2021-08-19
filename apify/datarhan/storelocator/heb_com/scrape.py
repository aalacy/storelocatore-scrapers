import csv
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()


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


@retry(stop=stop_after_attempt(5))
def fetch_locations(postal):
    url = "https://www.heb.com/commerce-api/v1/store/locator/address"
    headers = {
        "authority": "www.heb.com",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/json; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    body = {"address": postal, "curbsideOnly": False, "radius": 500}

    data = session.post(url, headers=headers, json=body).json()
    return data


MISSING = "<MISSING>"


def get(loc, key):
    return loc.get(key, MISSING) or MISSING


def fetch_data():
    scraped_items = []

    DOMAIN = "heb.com"
    search = DynamicZipSearch(
        max_radius_miles=50, country_codes=[SearchableCountries.USA]
    )

    for postal in search:
        data = fetch_locations(postal)

        for poi in data.get("stores", []):
            store = poi["store"]
            store_number = store["id"]
            if store_number in scraped_items:
                continue

            location_name = get(store, "name")
            street_address = get(store, "address1")
            city = get(store, "city")
            state = get(store, "state")
            zip_code = get(store, "postalCode")
            country_code = "US"
            location_type = MISSING
            phone = get(store, "phoneNumber")
            latitude = get(store, "latitude")
            longitude = get(store, "longitude")
            hours_of_operation = get(store, "storeHours")

            store_url = "https://www.heb.com/heb-store/US/{}/{}/{}-{}".format(
                state,
                city.replace(" ", "-"),
                location_name.replace(" ", "-"),
                store_number,
            )

            search.found_location_at(latitude, longitude)
            scraped_items.append(store_number)
            yield [
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

def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
