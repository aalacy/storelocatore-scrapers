import csv
import json

from bs4 import BeautifulSoup

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import sglog

from sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger(logger_name="siteone.com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    driver = SgChrome().chrome()
    data = []
    found = []

    locator_domain = "siteone.com"

    for i in range(100):
        base_link = (
            "https://www.siteone.com/store-finder?q=60101&miles=2000&page=%s" % i
        )
        log.info(base_link)
        driver.get(base_link)
        base = BeautifulSoup(driver.page_source, "lxml")

        try:
            stores = json.loads(base.text)["data"]
        except:
            break

        for store in stores:
            location_name = store["name"]
            street_address = (store["line1"] + " " + store["line2"]).strip()
            city = store["town"]
            state = store["regionCode"]
            zip_code = store["postalCode"]
            country_code = "US"
            store_number = store["storeId"]
            location_type = "<MISSING>"
            phone = store["phone"]

            hours = store["openings"]
            hours_of_operation = ""
            for day in hours:
                hours_of_operation = (
                    hours_of_operation + " " + day + " " + hours[day]
                ).strip()
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]

            link = "https://www.siteone.com/en/store/" + store_number
            found.append(link)

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

    if "https://www.siteone.com/en/store/396" not in found:
        driver = SgChrome().chrome()
        link = "https://www.siteone.com/en/store/396"
        log.info(link)
        driver.get(link)

        try:
            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.CLASS_NAME, "media-list"))
            )
        except TimeoutException:
            raise

        base = BeautifulSoup(driver.page_source, "lxml")

        script = (
            base.find("script", attrs={"type": "application/ld+json"})
            .text.replace("\n", "")
            .strip()
        )
        store = json.loads(script)

        location_name = store["name"]
        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        store_number = location_name.split("#")[-1]
        phone = store["address"]["telephone"]

        hours_of_operation = ""
        raw_hours = store["openingHoursSpecification"]
        for hours in raw_hours:
            day = hours["dayOfWeek"]
            opens = hours["opens"]
            closes = hours["closes"]
            if opens != "" and closes != "":
                clean_hours = day + " " + opens + "-" + closes
                hours_of_operation = (hours_of_operation + " " + clean_hours).strip()

        if "sat" not in hours_of_operation.lower():
            hours_of_operation = hours_of_operation + " SATURDAY CLOSED"

        if "sun" not in hours_of_operation.lower():
            hours_of_operation = hours_of_operation + " SUNDAY CLOSED"

        latitude = store["geo"]["latitude"]
        longitude = store["geo"]["longitude"]

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
