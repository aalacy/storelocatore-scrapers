import csv

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

log = SgLogSetup().get_logger("meijer.com")


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

    max_results = 40
    max_distance = 200

    dup_tracker = []

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    locator_domain = "meijer.com"

    for postcode in search:
        log.info(
            "Searching: %s | Items remaining: %s" % (postcode, search.items_remaining())
        )
        base_link = (
            "https://www.meijer.com/bin/meijer/store/search?locationQuery=%s&radius=%s"
            % (postcode, max_distance)
        )

        log.info(base_link)
        stores = session.get(base_link, headers=headers).json()["pointsOfService"]
        for store in stores:
            location_name = store["displayName"]
            street_address = store["address"]["line1"].strip()
            city = store["address"]["town"]
            state = store["address"]["region"]["isocode"].replace("US-", "")
            zip_code = store["address"]["postalCode"]
            country_code = "US"
            latitude = store["geoPoint"]["latitude"]
            longitude = store["geoPoint"]["longitude"]
            search.found_location_at(latitude, longitude)
            store_number = store["name"]
            if store_number in dup_tracker:
                continue
            dup_tracker.append(store_number)
            location_type = "<MISSING>"
            phone = store["phone"]
            hours_of_operation = "<INACCESSIBLE>"
            link = "<MISSING>"
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
