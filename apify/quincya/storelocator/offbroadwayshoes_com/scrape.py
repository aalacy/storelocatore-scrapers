import csv
import json

from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import SgLogSetup

from sgselenium import SgChrome

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


def fetch_data():
    page = 0
    found = []

    driver = SgChrome(executable_path='./chromedriver').driver()
    locator_domain = "rackroomshoes.com"
    run = True

    while run:
        base_link = f"https://www.rackroomshoes.com/store-finder?q=&page={page}&latitude=25.790654&longitude=-80.130045"

        driver.get(base_link)
        base = BeautifulSoup(driver.page_source, "lxml")

        result = json.loads(base.text)
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
            hours_of_operation = ",".join(
                f"{day} {openings[day]}" for day in openings)

            latitude = get(store, "latitude")
            longitude = get(store, "longitude")
            link = "https://www.rackroomshoes.com/store/" + store_number
            location_type = "Off Broadway Shoe Warehouse" if store['hideStore'] == 'true' else "Rack Room Shoes"

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
