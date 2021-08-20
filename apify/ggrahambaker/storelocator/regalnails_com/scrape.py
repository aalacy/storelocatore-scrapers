import csv
import time

from sglogging import SgLogSetup

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

logger = SgLogSetup().get_logger("regalnails_com")


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

    all_store_data = []
    dup_tracker = []

    max_results = 100
    max_distance = 300

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    locator_domain = "https://www.regalnails.com/"

    for lat, lng in search:
        logger.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        url = (
            "https://www.regalnails.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(lat)
            + "&lng="
            + str(lng)
            + "&max_results="
            + str(max_results)
            + "&search_radius="
            + str(max_distance)
            + "&filter=10"
        )

        try:
            res_json = session.get(url, headers=headers).json()
        except:
            time.sleep(5)
            res_json = session.get(url, headers=headers).json()

        for loc in res_json:
            location_name = loc["store"].replace("&#038;", "&")
            phone_number = loc["phone"].split("/")[0].replace("48w", "48")

            page_url = loc["url"]
            if page_url == "":
                page_url = "<MISSING>"
            lat = loc["lat"]
            longit = loc["lng"]
            if phone_number not in dup_tracker:
                dup_tracker.append(phone_number)
            else:
                continue

            search.found_location_at(lat, longit)

            street_address = loc["address"] + " " + loc["address2"]
            street_address = street_address.strip()

            city = loc["city"]
            state = loc["state"]
            zip_code = loc["zip"]
            if len(zip_code.split(" ")) == 2:
                country_code = "CA"
            else:
                if len(zip_code) == 6:
                    if "4505 E McKellips Road" in street_address:
                        zip_code = "<MISSING>"
                        country_code = "US"

                    else:
                        country_code = "CA"
                        zip_code = zip_code[:3] + " " + zip_code[3:]
                else:
                    country_code = "US"

            store_number = loc["id"].strip()
            if store_number == "":
                store_number = "<MISSING>"

            location_type = "<MISSING>"
            hours = "<MISSING>"

            if len(phone_number) < 5:
                phone_number = "<MISSING>"

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
