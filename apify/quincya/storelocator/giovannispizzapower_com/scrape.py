import csv

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="giovannispizzapower.com")


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

    session = SgRequests()
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "giovannispizzapower.com"

    found_poi = []

    max_results = 100
    max_distance = 500

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        url = (
            "https://giovannispizzapower.com/wp-admin/admin-ajax.php?action=store_search&lat=%s&lng=%s&max_results=%s&search_radius=%s"
            % (lat, lng, max_results, max_distance)
        )

        store_data = session.get(url, headers=headers).json()

        for store in store_data:
            page_url = store["url"]
            if not page_url:
                page_url = "<MISSING>"

            location_name = store["store"]
            street_address = (store["address"] + " " + store["address2"]).strip()
            city = store["city"]
            state = store["state"].replace("West Virginia", "WV")
            zip_code = store["zip"]
            country_code = store["country"]
            store_number = store["id"]

            if store_number not in found_poi:
                found_poi.append(store_number)
            else:
                continue

            location_type = "<MISSING>"
            phone = store["phone"]
            if not phone:
                phone = "<MISSING>"

            try:
                raw_hours = BeautifulSoup(store["hours"], "lxml")
                hours_of_operation = " ".join(list(raw_hours.stripped_strings))
            except:
                hours_of_operation = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lng"]
            search.found_location_at(latitude, longitude)

            yield [
                    locator_domain,
                    page_url,
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


scrape()
