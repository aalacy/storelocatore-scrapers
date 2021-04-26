import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="wirelesszone_com")


def write_output(data):
    with open("data.csv", newline="", mode="w", encoding="utf-8") as output_file:
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
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    locator_domain = "https://wirelesszone.com/"
    MAX_RESULTS = 100
    MAX_DISTANCE = 500

    dup_counter = []
    all_store_data = []
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=200
    )

    for lat, long in search:
        log.info(f"{(lat, long)} | remaining: {search.items_remaining()}")

        x = lat
        y = long

        url = (
            "https://wirelesszone.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(x)
            + "&lng="
            + str(y)
            + "&max_results="
            + str(MAX_RESULTS)
            + "&search_radius="
            + str(MAX_DISTANCE)
        )
        r = session.get(url, headers=HEADERS)

        res_json = json.loads(r.content)
        for loc in res_json:
            lat = loc["lat"]
            longit = loc["lng"]
            search.found_location_at(lat, longit)
            location_name = loc["store"]
            street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_code = loc["zip"]

            country_code = "US"

            phone_number = loc["phone"]
            page_url = "<MISSING>"

            store_number = loc["id"]
            if store_number not in dup_counter:
                dup_counter.append(store_number)
            else:
                continue

            phone_number = loc["phone"]
            hours = ""

            soup = BeautifulSoup(loc["hours"], "html.parser")
            hours_table = soup.find_all("td")
            for td in hours_table:
                hours += td.text + " "

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
