import csv

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicZipSearch, Grain_1_KM, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="marianos_com")

session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
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

    max_results = 50
    max_distance = 50

    addresses = []

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        granularity=Grain_1_KM(),
        max_search_distance_miles=max_distance,
        max_search_results=max_results,
    )

    log.info("Running sgzips..")
    base_url = "http://marianos.com/"

    for postcode in search:
        base_link = (
            "https://www.marianos.com/atlas/v1/stores/v1/search?filter.query="
            + str(postcode)
        )

        try:
            locations_json = session.get(base_link, headers=headers).json()["data"][
                "storeSearch"
            ]["results"]
        except:
            continue

        for script in locations_json:

            if "marianos" not in script["brand"].lower():
                continue
            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            page_url = ""
            hours_of_operation = ""

            raw_address = script["address"]["address"]
            street_address = " ".join(raw_address["addressLines"]).strip()
            city = raw_address["cityTown"]
            state = raw_address["stateProvince"]
            zipp = raw_address["postalCode"]
            country_code = raw_address["countryCode"]
            try:
                phone = script["phoneNumber"]
            except:
                phone = "<MISSING>"
            store_number = script["storeNumber"]
            latitude = script["location"]["lat"]
            longitude = script["location"]["lng"]
            search.found_location_at(latitude, longitude)
            location_name = script["vanityName"]
            location_type = "<MISSING>"
            page_url = (
                "https://www.marianos.com/stores/details/"
                + str(script["divisionNumber"])
                + "/"
                + str(script["storeNumber"])
            )

            hours_of_operation = ""
            raw_hours = script["formattedHours"]
            for raw_hour in raw_hours:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + raw_hour["displayName"]
                    + " "
                    + raw_hour["displayHours"]
                ).strip()
            hours_of_operation = hours_of_operation.replace("  ", " ")
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            store = [
                locator_domain,
                location_name,
                street_address,
                city,
                state,
                zipp,
                country_code,
                store_number,
                phone,
                location_type,
                latitude,
                longitude,
                hours_of_operation,
                page_url,
            ]
            if str(store[2]) not in addresses:
                addresses.append(str(store[2]))
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
