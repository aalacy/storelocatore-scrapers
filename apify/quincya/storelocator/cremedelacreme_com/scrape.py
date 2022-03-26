import csv

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("cremedelacreme_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    locator_domain = "cremedelacreme.com"

    found_poi = []
    data = []

    max_results = 100
    max_distance = 500

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:
        logger.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        base_link = (
            "https://cremedelacreme.com/wp-admin/admin-ajax.php?action=store_search&lat=%s&lng=%s&max_results=%s&search_radius=%s"
            % (lat, lng, max_results, max_distance)
        )
        stores = session.get(base_link, headers=headers).json()

        for store in stores:
            location_name = (
                store["store"].split(",")[0].replace("IL", "").split("&#")[0].strip()
            )
            if "OPENING SOON" in store["store"].upper():
                continue
            street_address = (store["address"] + " " + store["address2"]).strip()
            city = store["city"]
            state = store["state"]
            zip_code = store["zip"]
            country_code = "US"
            store_number = store["id"]

            if store_number not in found_poi:
                found_poi.append(store_number)
            else:
                continue

            location_type = "<MISSING>"
            phone = store["phone"]
            try:
                hours = BeautifulSoup(store["hours"], "lxml")
                hours_of_operation = " ".join(list(hours.stripped_strings))
            except:
                hours_of_operation = "<MISSING>"
            latitude = store["lat"]
            longitude = store["lng"]
            search.found_location_at(latitude, longitude)
            link = store["permalink"]

            data.append(
                [
                    locator_domain,
                    link,
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
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
