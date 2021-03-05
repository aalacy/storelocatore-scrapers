import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
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
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    max_results = 36
    max_distance = 20

    dup_tracker = []

    locator_domain = "partycity.ca"

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:

        base_link = (
            "https://api-triangle.partycity.ca/dss/services/v5/stores?lang=en&radius=%s&maxCount=%s&includeServicesData=false&lat=%s&lng=%s&storeType=store"
            % (max_distance, max_results, lat, lng)
        )
        stores = session.get(base_link, headers=headers).json()

        for store in stores:

            if "PTY" not in store["storeType"]:
                continue

            store_number = store["storeNumber"]
            if store_number in dup_tracker:
                continue

            dup_tracker.append(store_number)
            latitude = store["storeLatitude"]
            longitude = store["storeLongitude"]

            search.found_location_at(latitude, longitude)

            location_name = store["storeName"]
            street_address = store["storeAddress1"]
            city = store["storeCityName"]
            state = store["storeProvince"]
            zip_code = store["storePostalCode"]
            country_code = "CA"
            location_type = "<MISSING>"
            phone = store["storeTelephone"]

            link = "https://www.partycity.ca/en/store-details/%s/%s.store.html" % (
                state.lower(),
                store["storeCrxNodeName"],
            )

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            hours_of_operation = ""
            raw_hours = base.find(
                class_="store-locator__store-info__hours-table"
            ).find_all("tr")
            for raw_hour in raw_hours:
                day = raw_hour.find(
                    class_="store-locator__store-info__hours-table__day"
                ).text
                hours_js = json.loads(raw_hour["data-working-hours"])
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + day
                    + " "
                    + hours_js["open"]
                    + "-"
                    + hours_js["close"]
                ).strip()

            # Store data
            yield [
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


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
