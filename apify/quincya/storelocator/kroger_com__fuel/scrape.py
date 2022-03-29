import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, Grain_1_KM, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="kroger.com")


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
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    locator_domain = "kroger.com"

    max_results = 50
    max_distance = 40

    dup_tracker = []

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        granularity=Grain_1_KM(),
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )

    log.info("Running sgzips..")

    for postcode in search:
        base_link = (
            "https://www.kroger.com/atlas/v1/stores/v1/search?filter.query="
            + str(postcode)
        )

        try:
            locs = session.get(base_link, headers=headers).json()["data"][
                "storeSearch"
            ]["results"]
        except:
            continue

        for loc in locs:

            if "KROGER" not in loc["brand"].upper():
                continue
            if ("gas" not in str(loc).lower()) and ("diesel" not in str(loc).lower()):
                continue

            page_url = (
                "https://www.kroger.com/stores/details/"
                + loc["loyaltyDivisionNumber"]
                + "/"
                + loc["storeNumber"]
            )

            location_name = loc["vanityName"] + " " + loc["facilityName"]

            lat = loc["location"]["lat"]
            lng = loc["location"]["lng"]
            search.found_location_at(lat, lng)

            store_number = loc["locationId"]
            if store_number not in dup_tracker:
                dup_tracker.append(store_number)
            else:
                continue

            raw_address = loc["address"]["address"]
            street_address = " ".join(raw_address["addressLines"]).strip()
            city = raw_address["cityTown"]
            state = raw_address["stateProvince"]
            zip_code = raw_address["postalCode"]
            country_code = raw_address["countryCode"]
            try:
                phone_number = loc["phoneNumber"]
            except:
                phone_number = "<MISSING>"
            location_type = "<MISSING>"

            hours = ""
            raw_hours = loc["formattedHours"]
            for raw_hour in raw_hours:
                hours = (
                    hours
                    + " "
                    + raw_hour["displayName"]
                    + " "
                    + raw_hour["displayHours"]
                ).strip()
            hours = hours.replace("  ", " ")

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
                lng,
                hours,
                page_url,
            ]
            yield store_data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
