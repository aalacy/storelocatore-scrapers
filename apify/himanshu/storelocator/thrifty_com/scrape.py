import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

logger = SgLogSetup().get_logger("thrifty_com")
session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def fetch_data():
    tracker = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    base_url = "https://www.thrifty.com/"
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_results=20,
        max_radius_miles=100,
    )
    for zip_code in search:
        page_url = f"https://www.thrifty.com/loc/modules/multilocation/?near_location={zip_code}&services__in=&published=1&within_business=true"

        try:
            json_r = session.get(page_url, headers=headers).json()
        except:
            continue

        for data in json_r["objects"]:
            store_number = data["id"]
            if store_number in tracker:
                continue
            tracker.append(store_number)

            location_type = "Thrifty"
            location_name = get(data, "location_name")
            street_address = get(data, "street")
            city = get(data, "city")
            state = get(data, "state")
            zipp = get(data, "postal_code")
            country_code = get(data, "country")
            if country_code not in ["CA", "US"]:
                continue
            phone = get(data["phonemap"], "phone")
            latitude = get(data, "lat")
            longitude = get(data, "lon")
            page_url = get(data, "location_url")

            hours = data["formatted_hours"]["primary"]["days"]
            HOO = [f"{hour['label']} {hour['content']}" for hour in hours]
            hours_of_operations = ",".join(HOO) if len(HOO) else MISSING

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operations)
            store.append(page_url)

            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
