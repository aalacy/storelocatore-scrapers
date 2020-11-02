import csv
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


COMPANY_URL = "https://www.sonesta.com"
CHROME_DRIVER_PATH = "chromedriver"


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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    latitude_list = []
    longitude_list = []
    phone_numbers = []
    data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Fetch ajax
    location_url = "https://www.sonesta.com/api/property_listing"
    driver.get(location_url)
    wait = WebDriverWait(driver, 10)
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "pre")))

    listings = json.loads(driver.find_element_by_tag_name("pre").text)

    for listing in listings:
        if listing["country"] == "United States":
            locations_titles.append(listing["title"])
            street_addresses.append("address")
            cities.append(listing["city"])
            states.append(listing["state"])
            latitude_list.append(listing["geo_lat"])
            longitude_list.append(listing["geo_lon"])

            # Nav to location to get extra information
            driver.get(listing["url"])

            # Wait until element appears - 10 secs max
            wait = WebDriverWait(driver, 10)
            wait.until(
                ec.visibility_of_element_located(
                    (By.CSS_SELECTOR, ".footer-primary__left")
                )
            )

            phone_numbers.append(
                driver.find_element_by_css_selector("a.footer-primary__number-link")
                .get_attribute("textContent")
                .strip()
            )
            zip_codes.append(
                driver.find_element_by_css_selector("span.postal-code")
                .get_attribute("textContent")
                .strip()
            )

    # Store data
    for (
        locations_title,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        latitude,
        longitude,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                "US",
                "<MISSING>",
                phone_number,
                "<MISSING>",
                latitude,
                longitude,
                "Always open",
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
