import csv
import json
import time

from bs4 import BeautifulSoup

from sglogging import sglog

from sgselenium import SgChrome

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

log = sglog.SgLogSetup().get_logger(logger_name="daylightdonuts.com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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

    driver = SgChrome(user_agent=user_agent).driver()

    locator_domain = "daylightdonuts.com"

    found_poi = []

    max_results = 100
    max_distance = 100

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=max_distance,
        max_search_results=max_results,
    )

    for lat, lng in search:
        log.info(
            "Searching: %s, %s | Items remaining: %s"
            % (lat, lng, search.items_remaining())
        )

        url = (
            "http://www.daylightdonuts.com/wp-admin/admin-ajax.php?action=store_search&lat=%s&lng=%s&max_results=%s&search_radius=%s&_=1564199818851"
            % (lat, lng, max_results, max_distance)
        )

        driver.get(url)
        time.sleep(1)
        base = BeautifulSoup(driver.page_source, "lxml")

        try:
            store_data = json.loads(base.text)
        except:
            continue

        for store in store_data:
            page_url = store["url"]
            if not page_url:
                page_url = "<MISSING>"

            location_name = store["store"].replace("#038;", "")
            street_address = (store["address"] + " " + store["address2"]).strip()
            city = store["city"]
            state = store["state"]
            zip_code = store["zip"]
            country_code = "US"
            store_number = store["id"]

            if store_number not in found_poi:
                found_poi.append(store_number)
            else:
                continue

            location_type = "<MISSING>"
            phone = store["phone"].split("or")[0].strip()
            if not phone[-2:].isdigit():
                phone = "<MISSING>"

            try:
                raw_hours = BeautifulSoup(store["hours"], "lxml")
                hours_of_operation = " ".join(list(raw_hours.stripped_strings))
            except:
                hours_of_operation = "<MISSING>"

            latitude = store["lat"]
            longitude = store["lng"]
            search.found_location_at(latitude, longitude)

            yield [
                locator_domain,
                page_url,
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
    driver.close()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
