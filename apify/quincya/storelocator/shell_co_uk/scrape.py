import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="shell.co.uk")


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

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []
    found_poi = []

    locator_domain = "shell.co.uk"

    max_results = None
    max_distance = 100

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        base_link = (
            "https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat=%s&lng=%s&autoload=true&&corridor_radius=%s&format=json"
            % (lat, lng, max_distance)
        )

        stores = session.get(base_link, headers=headers).json()

        new_coordinates = []
        for store in stores:
            location_name = (store["brand"] + " " + store["name"]).upper()
            street_address = store["address"].strip()
            city = store["city"]
            state = store["state"]
            zip_code = store["postcode"]
            country_code = store["country_code"]
            if country_code != "GB":
                continue
            store_number = store["id"]
            if store_number in found_poi:
                continue
            found_poi.append(store_number)
            location_type = ", ".join(store["fuels"])
            if not location_type:
                location_type = "<MISSING>"
            phone = store["telephone"]
            if store["open_status"] == "twenty_four_hour":
                hours_of_operation = "Open 24 Hours"
            else:
                hours_of_operation = "<INACCESSIBLE>"

            latitude = store["lat"]
            longitude = store["lng"]
            new_coordinates.append([latitude, longitude])

            link = store["website_url"]

            # Store data
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

        if len(new_coordinates) > 0:
            search.mark_found(new_coordinates)
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
