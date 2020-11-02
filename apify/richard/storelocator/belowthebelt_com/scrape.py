import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


COMPANY_URL = "https://www.belowthebelt.com/"
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
    phone_numbers = []
    data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get("https://www.belowthebelt.com/pages/stores")

    # Wait until element appears - 10 secs max
    wait = WebDriverWait(driver, 10)
    wait.until(
        ec.visibility_of_element_located((By.CSS_SELECTOR, "div.storelocator-panel"))
    )

    while True:
        if len(driver.find_elements_by_css_selector("div.store")) > 0:
            stores = driver.find_elements_by_css_selector("div.store")
            break

    for store in stores:
        # Location title
        locations_titles.append(
            store.find_element_by_css_selector("div.title").get_attribute("textContent")
        )

        # Street address
        street_addresses.append(
            store.find_element_by_css_selector("div.address")
            .get_attribute("innerHTML")
            .split("<br>")[1]
            .replace("<span>", "")
            .replace("</span>", "")
        )

        # City
        cities.append(
            store.find_element_by_css_selector("div.address")
            .get_attribute("innerHTML")
            .split("<br>")[2]
            .split(",")[0]
            .strip()
        )

        # Province
        states.append(
            store.find_element_by_css_selector("div.address")
            .get_attribute("innerHTML")
            .split("<br>")[2]
            .split(",")[1]
            .strip()[:-7]
            .strip()
        )

        # Zip code
        zip_codes.append(
            store.find_element_by_css_selector("div.address")
            .get_attribute("innerHTML")
            .split("<br>")[2]
            .split(",")[1]
            .strip()[-7:]
            .strip()
        )

        # phone
        phone_numbers.append(
            store.find_element_by_css_selector("div.phone").get_attribute("textContent")
        )

    # Store data
    for (locations_title, street_address, city, state, zipcode, phone_number) in zip(
        locations_titles, street_addresses, cities, states, zip_codes, phone_numbers
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                "CA",
                "<MISSING>",
                phone_number,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
