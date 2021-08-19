import csv

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="dekalash.com")


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    found_poi = []
    data = []

    max_results = 100
    max_distance = 1000

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )
        api_link = (
            "https://api.storepoint.co/v1/15e2b4dd23ff14/locations?lat=%s&long=%s&radius=%s"
            % (lat, lng, max_distance)
        )

        store_data = session.get(api_link, headers=headers).json()["results"][
            "locations"
        ]
        if not store_data:
            continue

        locator_domain = "dekalash.com"

        for store in store_data:
            store_number = store["id"]
            if store_number in found_poi:
                continue
            found_poi.append(store_number)

            link = store["website"]
            location_name = store["name"]
            raw_address = store["streetaddress"].split(",")[:-1]
            street_address = " ".join(raw_address[:-2]).strip().replace("  ", " ")
            city = raw_address[-2].strip()
            state = raw_address[-1].split()[0].strip()
            zip_code = raw_address[-1].split()[1].strip()
            country_code = store["streetaddress"].split(",")[-1].strip()
            location_type = "<MISSING>"

            if "4346 Belden Village" in street_address:
                zip_code = "44718"

            phone = store["phone"]
            if not phone:
                phone = "<MISSING>"

            latitude = store["loc_lat"]
            longitude = store["loc_long"]
            search.found_location_at(latitude, longitude)

            log.info(link)
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            if "coming soon" in base.find(class_="elementor-row").text.lower():
                continue

            if "temporarily closed" in base.find(class_="elementor-row").text.lower():
                hours_of_operation = "Temporarily Closed"
            else:
                hours_of_operation = " ".join(
                    list(base.find(class_="IiXf4c").stripped_strings)
                )

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
