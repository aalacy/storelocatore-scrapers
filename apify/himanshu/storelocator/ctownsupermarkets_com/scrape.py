import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="ctownsupermarkets.com")

session = SgRequests()
MISSING = "<MISSING>"


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def format_hours(hours_of_operations):
    days = []
    for day, hours in hours_of_operations.items():
        if hours.get("isClosed"):
            continue

        day_hours = hours.get("openIntervals", [])[0]
        days.append(day + " " + day_hours["start"] + "-" + day_hours["end"])

    return ",".join(days) or MISSING


def fetch_data():
    max_count = 50
    max_distance = 50
    found_poi = []

    log.info("Running sgzip..")

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_count,
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
    }

    for zip_code in search:

        locator_domain = "ctownsupermarkets.com"
        location_map = {}

        params = {
            "location": zip_code,
            "limit": max_count,
            "radius": max_distance,
            "v": 20181201,
            "entityTypes": "location",
            "resolvePlaceholders": True,
            "api_key": "ae29ff051811d0bf52d721ab2cadccb8",
            "savedFilterIds": "29721495",
        }

        location_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch"
        data = session.get(location_url, headers=headers, params=params).json()
        locations = data["response"]["entities"]
        for location in locations:
            store_number = location["meta"]["id"]

            phone = location.get("mainPhone", MISSING)

            if phone not in found_poi:
                found_poi.append(phone)
            else:
                continue

            page_url = location["c_baseWebsiteURL"]

            address = location["address"]
            street_address = address.get("line1", MISSING)
            city = address.get("city", MISSING)
            state = address.get("region", MISSING)
            postal = address.get("postalCode", MISSING)
            country_code = address.get("countryCode", MISSING)

            coordinate = location.get("geocodedCoordinate", {})
            latitude = coordinate.get("latitude", MISSING)
            longitude = coordinate.get("longitude", MISSING)

            if latitude != MISSING and longitude != MISSING:
                search.found_location_at(latitude, longitude)

            page_url = location.get("websiteUrl", {}).get("url", MISSING)

            location_type = location.get("services", [MISSING])[0]
            location_name = location.get("name")
            hours_of_operation = format_hours(location.get("hours"))

            store = []
            store.append(locator_domain)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(postal)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)

            location_map[store_number] = True

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
