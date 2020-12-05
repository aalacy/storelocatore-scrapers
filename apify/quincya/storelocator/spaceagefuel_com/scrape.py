import csv
import json
from bs4 import BeautifulSoup
from sgselenium import SgChrome
import time
from sglogging import sglog


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

    log = sglog.SgLogSetup().get_logger(logger_name="spaceagefuel.com")

    base_link = "http://spaceagefuel.com/wp-json/store-locator-plus/v2/locations/"

    driver = SgChrome().chrome()

    driver.get(base_link)

    log.debug(driver.page_source)

    base = BeautifulSoup(driver.page_source, "lxml")

    sl_ids = json.loads(base.text)

    data = []
    locator_domain = "spaceagefuel.com"

    for sl_id in sl_ids:
        store_link = base_link + sl_id["sl_id"]

        driver = SgChrome().chrome()
        driver.get(store_link)

        time.sleep(5)
        base = BeautifulSoup(driver.page_source, "lxml")

        log.debug(base.text)

        store = json.loads(base.text)
        location_name = store["sl_store"].replace("amp;", "")
        street_address = (store["sl_address"] + " " + store["sl_address2"]).strip()
        city = store["sl_city"]
        state = store["sl_state"]
        zip_code = store["sl_zip"]
        country_code = "US"
        store_number = store["sl_id"]
        location_type = "<MISSING>"
        phone = store["sl_phone"]
        hours_of_operation = "<MISSING>"
        latitude = store["sl_latitude"]
        longitude = store["sl_longitude"]
        if not latitude:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        link = store["sl_url"]
        if not link:
            link = "<MISSING>"

        # Store data
        data.append(
            [
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
        )

        driver.close()

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
