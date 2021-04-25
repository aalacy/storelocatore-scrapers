import csv
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("scotiabank_com")


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

    max_results = 50
    max_distance = None
    dup_tracker = []
    total = 0
    locator_domain = "scotiabank.com"

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )
    for lat, lng in search:
        base_link = (
            "https://mapsms.scotiabank.com/branches?1=1&latitude=%s&longitude=%s&recordlimit=%s&locationtypes=1,2,3"
            % (lat, lng, "50")
        )
        try:
            stores = session.get(base_link, headers=headers).json()["branchInfo"][
                "marker"
            ]
        except Exception as e:
            print(session.get(base_link, headers=headers).text)
            print(e)
            continue
        logger.info(f"Pulling the data from: {base_link}")
        found = 0
        print(len(stores))
        for store in stores:
            store_number = store["@attributes"]["id"]
            latitude = store["@attributes"]["lat"]
            longitude = store["@attributes"]["lng"]

            search.found_location_at(latitude, longitude)
            if store_number in dup_tracker:
                continue
            dup_tracker.append(store_number)

            location_name = store["name"]
            location_type = "Branch" if store["@attributes"]["type"] == "1" else "ABM" if store["@attributes"]["type"] == "3" else store["@attributes"]["type"]
            print(location_type)
            street_address = " ".join(store["address"].split(",")[:-3])
            city = store["address"].split(",")[-3].strip()
            if len(store["address"].split(",")[-2].split()) > 1:
                state = store["address"].split(",")[-2].strip()[:-7].strip()
                zip_code = store["address"].split(",")[-2].strip()[-7:].strip()
            else:
                state = store["address"].split(",")[-2].strip()
                zip_code = "<MISSING>"
            country_code = "CA"
            phone = store["phoneNo"]
            if not phone:
                phone = "<MISSING>"

            hours = store["hours"]
            hours_of_operation = ""
            for day in hours:
                try:
                    day_hr = hours[day]["open"] + "-" + hours[day]["close"]
                except:
                    day_hr = "Closed"
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + day_hr
                ).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "<MISSING>"

            # Store data
            yield [
                locator_domain,
                "<MISSING>",
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
            found += 1
        total += found
    logger.info(f"Scraping Finished | Total Store Count:{total}")


def scrape():
    logger.info("Scraping Started!")
    data = fetch_data()
    write_output(data)


scrape()
