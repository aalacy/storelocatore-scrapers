import csv
import re

from sglogging import sglog

from sgrequests import SgRequests

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="lindt.ca")


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
    locator_domain = "lindt.ca"

    max_results = 8
    max_distance = 200

    dup_tracker = set()

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    base_link = "https://lindt.locator.cloud/core_functions/ajaxdata.php"

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        payload = {
            "type": "getplacedata",
            "locator_id": "63",
            "client_id": "62",
            "table_postfix": "lindt",
            "lang": "en",
            "lat": lat,
            "lng": lng,
            "radius": max_distance,
            "limit": max_results,
            "topic": "22,25,23,24,29",
        }

        res_json = session.post(base_link, headers=headers, data=payload).json()["data"]

        for loc in res_json:

            location_name = loc["place_name"].strip()

            store_number = loc["uid"]
            if store_number not in dup_tracker:
                dup_tracker.add(store_number)
            else:
                continue

            phone_number = loc["phone_number"]
            if not phone_number:
                phone_number = "<MISSING>"

            lat = loc["lat_individual"]
            longit = loc["lng_individual"]
            search.found_location_at(lat, longit)

            raw_address = (
                loc["short_description"]
                .replace("\r\n", "")
                .replace("Suite 211 Vaughan", "Suite 211, Vaughan")
                .replace("Gare Vaudreuil", "Gare, Vaudreuil")
                .replace("St N Waterloo", "St N, Waterloo")
                .replace("New Brunswick, E1", "NewBrunswick E1")
                .replace(" Québec", " ,Québec")
                .replace('<span style="font-size: 16px; ">', "")
                .replace("Les Avenues Vaudreuil -", "")
                .replace("Carrefour Laval", "Carrefour, Laval")
                .replace("<br />", ",")
                .split("&nbsp")[0]
                .split(",")
            )

            if raw_address[0] == "":
                raw_address.pop(0)

            if "CANADA" in raw_address[-1].upper():
                raw_address.pop(-1)
            street_address = " ".join(raw_address[:-2]).strip()
            if ">" in street_address:
                street_address = street_address.split(">")[1].strip()
            city = raw_address[-2].replace("</span>", "").replace("No. 44", "").strip()
            state = raw_address[-1].split()[0].strip()
            zip_code = raw_address[-1].replace(state, "").replace("</span>", "").strip()
            state = state.replace("New", "New ")
            if "Unit" in city or "Suite" in city:
                street_address = (
                    street_address + " " + " ".join(city.split()[:2]).strip()
                )
                city = " ".join(city.split()[2:]).strip()

            street_address = (re.sub(" +", " ", street_address)).strip()

            if "5401 Boulevard" in street_address:
                street_address = street_address.replace("Québec", "").strip()
                city = "Québec"
                state = "QC"
                zip_code = "G2K 1N4"

            if "#2058" not in street_address and "Mode Unit" not in street_address:
                try:
                    digit = re.search(r"\d", street_address).start(0)
                    if digit != 0:
                        street_address = street_address[digit:]
                except:
                    pass

            country_code = "CA"
            hours = loc["further_information_content"].replace("\r\n", " ").strip()
            page_url = "<MISSING>"
            location_type = "<MISSING>"

            if "Temporarily" in loc["suggestion"]:
                hours = "Temporarily Closed"

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

            yield store_data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
