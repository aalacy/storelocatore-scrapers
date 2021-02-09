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


def fetch_data():

    driver = SgChrome().chrome()

    data = []
    found = []
    locator_domain = "rackroomshoes.com"

    total = 1000

    for i in range(150):

        if len(data) == int(total):
            break

        base_link = (
            "https://www.rackroomshoes.com/store-finder?q=&page=%s&latitude=25.790654&longitude=-80.130045"
            % (i)
        )
        print(base_link)
        driver.get(base_link)
        base = BeautifulSoup(driver.page_source, "lxml")

        stores = json.loads(base.text)["data"]
        total = json.loads(base.text)["total"]

        for store in stores:
            location_name = store["displayName"]
            street_address = store["line1"].strip()
            city = store["town"]
            state = store["city"]
            zip_code = store["postalCode"]
            country_code = store["country"]
            store_number = store["name"]
            phone = store["phone"]
            hours_of_operation = ""
            raw_hours = store["openings"]
            for hour in raw_hours:
                hours_of_operation = (
                    hours_of_operation + " " + hour + " " + raw_hours[hour]
                ).strip()
            latitude = store["latitude"]
            longitude = store["longitude"]
            link = "https://www.rackroomshoes.com/store/" + store_number
            if link in found:
                continue
            found.append(link)

            driver.get(link)

            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.CLASS_NAME, "store-logo"))
            )

            base = BeautifulSoup(driver.page_source, "lxml")
            location_type = base.find(class_="store-logo")["alt"]

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
