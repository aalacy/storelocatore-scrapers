import csv
import json
import time

from tenacity import retry, stop_after_attempt
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgselenium import SgChrome

log = SgLogSetup().get_logger("meijer.com")


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


@retry(stop=stop_after_attempt(5))
def fetch_page(page, driver):
    data = []
    base_link = f"https://www.meijer.com/shop/en/store-finder/search?q=60010&page={page}&radius=4500"

    log.info(base_link)
    driver.get(base_link)
    time.sleep(1)

    base = BeautifulSoup(driver.page_source, "lxml")
    stores = json.loads(base.text)["data"]

    locator_domain = "meijer.com"

    for store in stores:
        location_name = store["displayName"]
        street_address = (store["line1"] + " " + store["line2"]).strip()
        city = store["town"]
        state = store["state"]
        zip_code = store["postalCode"]
        country_code = "US"
        store_number = store["name"]
        location_type = "<MISSING>"
        phone = store["phone"]
        hours_of_operation = "<INACCESSIBLE>"
        latitude = store["latitude"]
        longitude = store["longitude"]
        link = "https://www.meijer.com/shop/en/store/" + store_number

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

    return data


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()

    data = []

    for page_num in range(50):
        locations = fetch_page(page_num, driver)
        data.extend(locations)

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
