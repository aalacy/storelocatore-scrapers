import csv

from bs4 import BeautifulSoup

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from sglogging import sglog

from sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger(logger_name="landrover.co.uk")


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
    found_poi = []
    restart_driver = False

    locator_domain = "landrover.co.uk"

    cities = ["london", "plymouth", "swansea", "manchester", "carlisle", "inverness"]
    for num, i in enumerate(cities):
        base_link = (
            "https://www.landrover.co.uk/national-dealer-locator.html?placeName=%s&radius=100&filter=All"
            % i
        )

        if not restart_driver and num > 2:
            restart_driver = True
            driver.close()
            driver = SgChrome().chrome()

        log.info(base_link)
        driver.get(base_link)

        base = BeautifulSoup(driver.page_source, "lxml")

        try:
            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.CLASS_NAME, "cardTitle"))
            )
        except TimeoutException:
            driver.close()
            driver = SgChrome().chrome()

            driver.get(base_link)

            base = BeautifulSoup(driver.page_source, "lxml")

            WebDriverWait(driver, 50).until(
                ec.presence_of_element_located((By.CLASS_NAME, "cardTitle"))
            )

        items = base.find_all(class_="infoCardDealer infoCard")

        for item in items:
            location_name = item.find(
                class_="dealerNameText fontBodyCopyLarge"
            ).text.strip()

            try:
                link = item.find(class_="primaryLinkWithStyle")["href"]

                if link in found_poi:
                    continue
                found_poi.append(link)
            except:
                link = "<MISSING>"

            raw_address = item.find(class_="addressText").text.split(",")
            zip_code = raw_address[-1].strip()

            if len(raw_address[:-1]) == 3:
                street_address = raw_address[0].strip()
                city = raw_address[1].strip()
                state = raw_address[2].strip()

            elif len(raw_address[:-1]) == 2:
                street_address = raw_address[0].strip()
                city = "<MISSING>"
                state = raw_address[1].strip()

            elif len(raw_address[:-1]) == 1:
                street_address = raw_address[0].strip()
                city = "<MISSING>"
                state = "<MISSING>"

            elif len(raw_address[:-1]) > 3:
                street_address = " ".join(raw_address[:-3]).strip().replace("  ", " ")
                city = raw_address[-3].strip()
                state = raw_address[-2].strip()

            if location_name + street_address in found_poi:
                continue
            found_poi.append(location_name + street_address)

            country_code = "GB"
            store_number = item["data-ci-code"]

            try:
                location_type = ", ".join(
                    list(item.find(class_="services").stripped_strings)
                ).replace(
                    "LAND ROVER TO YOU, Too busy to come to us?, Try Land Rover to You",
                    "LAND ROVER TO YOU",
                )
            except:
                location_type = "<MISSING>"

            try:
                phone = item.find(class_="phoneNumber").text.strip()
            except:
                phone = "<MISSING>"
            hours_of_operation = "INACCESSIBLE"
            latitude = item["data-lat"]
            longitude = item["data-lng"]

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
