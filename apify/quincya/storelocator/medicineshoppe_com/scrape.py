import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="medicineshoppe.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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


def fetch_data():
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    }
    locator_domain = "medicineshoppe.com"

    max_results = 10
    max_distance = 100

    all_store_data = []

    dup_tracker = []

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    base_link = "https://api-web.rxwiki.com/api/v2/location/search"

    i = 1
    for postcode in search:
        json = {
            "search_radius": max_distance,
            "query": postcode,
            "page": "0",
            "app_id": "2faa9d19-602f-4342-a44f-e2a8c7df2797",
        }
        log.info(
            "Searching: %s | Items remaining: %s" % (postcode, search.items_remaining())
        )
        # Reset every 20 to avoid Too many requests block
        if i % 20 == 0:
            session = SgRequests()
        i += 1

        res_json = session.post(base_link, headers=headers, json=json).json()[
            "locations"
        ]

        for loc in res_json:

            location_name = loc["name"].strip()

            phone_number = loc["phone"]
            if phone_number not in dup_tracker:
                dup_tracker.append(phone_number)
            else:
                continue

            lat = loc["latitude"]
            longit = loc["longitude"]
            search.found_location_at(lat, longit)

            raw_address = loc["addr"]["Main"]
            try:
                street_address = (
                    raw_address["street1"] + " " + raw_address["street2"]
                ).strip()
            except:
                street_address = raw_address["street1"]
            street_address = (
                street_address.replace("Ventura, CA", "").replace("  ", " ").strip()
            )
            city = raw_address["city"]
            state = raw_address["state"]
            zip_code = raw_address["zip"]
            if len(zip_code) < 5:
                zip_code = "0" + zip_code

            country_code = "US"

            store_number = "<MISSING>"

            hours = ""
            raw_hours = loc["hours"]
            for raw_hour in raw_hours:
                if raw_hour["day"] == 1:
                    day = "Mon"
                if raw_hour["day"] == 2:
                    day = "Tue"
                if raw_hour["day"] == 3:
                    day = "Wed"
                if raw_hour["day"] == 4:
                    day = "Thu"
                if raw_hour["day"] == 5:
                    day = "Fri"
                if raw_hour["day"] == 6:
                    day = "Sat"
                if raw_hour["day"] == 7:
                    day = "Sun"
                hours = (
                    hours
                    + " "
                    + day
                    + " "
                    + str(raw_hour["startHH"])
                    + ":"
                    + str(raw_hour["startMM"])
                    + "-"
                    + str(raw_hour["endHH"])
                    + ":"
                    + str(raw_hour["endMM"])
                ).strip()
            if "Sat" not in hours:
                hours = hours + " Sat Closed"
            if "Sun" not in hours:
                hours = hours + " Sun Closed"

            hours = (
                hours.replace("21:0-", "9:0-")
                .replace(":0 ", ":00 ")
                .replace(":0-", ":00-")
                .strip()
            )
            if hours[-2:] == ":0":
                hours = hours + "0"

            try:
                page_url = loc["custUrl"]["Main"]["url"]
            except:
                page_url = "<MISSING>"

            if not page_url:
                page_url = "<MISSING>"

            location_type = "<MISSING>"

            store_data = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
                store_number,
                phone_number,
                location_type,
                lat,
                longit,
                hours,
                page_url,
            ]

            all_store_data.append(store_data)

    return all_store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
