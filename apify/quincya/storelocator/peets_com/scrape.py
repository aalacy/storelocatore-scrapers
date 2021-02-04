import csv
import json

from bs4 import BeautifulSoup

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="peets.com")


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

    max_results = 25
    max_distance = 30

    dup_tracker = []

    data = []
    locator_domain = "peets.com"

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    log.info("Searching zip_codes ..")

    for lat, lng in search:
        base_link = (
            "https://stockist.co/api/v1/u5687/locations/search?callback=jQuery214012681410710237628_1612239285797&tag=u5687&latitude=%s&longitude=%s&distance=%s"
            % (lat, lng, max_distance)
        )

        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        js = base.text.split('locations":')[1].split(',"debug"')[0]
        stores = json.loads(js)

        result_coords = []

        for store in stores:

            if "peet" not in store["custom_fields"][0]["value"].lower():
                continue

            store_number = store["id"]
            if store_number in dup_tracker:
                continue
            dup_tracker.append(store_number)

            latitude = store["latitude"]
            longitude = store["longitude"]

            result_coords.append([latitude, longitude])

            location_name = store["name"]
            street_address = store["address_line_1"]
            city = store["city"]
            state = store["state"]
            zip_code = store["postal_code"]
            country_code = "US"
            location_type = "<MISSING>"
            phone = store["phone"]

            raw_hours = store["custom_fields"]
            hours_of_operation = ""
            for raw_hour in raw_hours:
                if "hour" in str(raw_hour).lower():
                    hours_of_operation = (
                        hours_of_operation
                        + " "
                        + raw_hour["name"].replace("Hours:", "").strip()
                        + " "
                        + raw_hour["value"]
                    ).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            link = "<MISSING>"

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

        if len(result_coords) > 0:
            search.mark_found(result_coords)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
