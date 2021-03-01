import csv
import json
import time
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgselenium import SgChrome
from tenacity import retry, stop_after_attempt

log = SgLogSetup().get_logger("offbroadwayshoes.com")


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


MISSING = "<MISSING>"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def get_location_type(store):
    hide_store = store["hideStore"] == "true"
    if hide_store:
        return "Off Broadway Shoe Warehouse"
    else:
        return "Rack Room Shoes"


@retry(stop=stop_after_attempt(3))
def fetch_page(page, driver):
    base_link = f"https://www.rackroomshoes.com/store-finder?q=&page={page}&latitude=25.790654&longitude=-80.130045"
    driver.get(base_link)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "lxml")
    return json.loads(soup.text)


def fetch_data():
    page = 0
    found = []

    driver = SgChrome().driver()
    locator_domain = "rackroomshoes.com"
    run = True

    while run:
        result = fetch_page(page, driver)
        stores = result["data"]
        total = result["total"]

        for store in stores:
            store_number = get(store, "name")
            if store_number in found:
                continue
            found.append(store_number)

            location_name = get(store, "displayName")
            street_address = get(store, "line1").strip()
            city = get(store, "town")
            state = get(store, "city")
            zip_code = get(store, "postalCode")
            country_code = get(store, "country")
            phone = get(store, "phone")

            openings = store["openings"]
            hours_of_operation = ",".join(f"{day} {openings[day]}" for day in openings)

            latitude = get(store, "latitude")
            longitude = get(store, "longitude")
            link = "https://www.rackroomshoes.com/store/" + store_number
            location_type = get_location_type(store)

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

        if len(found) >= total:
            run = False
        else:
            page += 1

    driver.close()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
