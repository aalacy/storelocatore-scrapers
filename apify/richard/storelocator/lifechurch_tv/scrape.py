import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


COMPANY_URL = "https://www.life.church"
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
    hours = []
    data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Fetch store urls from location menu
    location_url = "https://www.life.church/locations/?utm_source=life.church&utm_medium=website&utm_content=Header-Locations&utm_campaign=Life.Church"
    driver.get(location_url)

    # Wait until element appears - 10 secs max
    wait = WebDriverWait(driver, 10)
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, ".location-state")))

    location_urls = [
        location_url.get_attribute("href")
        for location_url in driver.find_elements_by_css_selector("a.campus-link")
    ]

    for location_url in location_urls:
        driver.get(location_url)

        try:
            # Wait until element appears - 10 secs max
            wait = WebDriverWait(driver, 10)
            wait.until(
                ec.visibility_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        ".small-12.large-4.large-offset-1.columns.campus-info.m-b-4",
                    )
                )
            )
        except:
            continue

        location_title = driver.find_element_by_css_selector(
            "span.campus-name"
        ).get_attribute("textContent")
        street_address = (
            driver.find_element_by_css_selector(
                "a.campus-address > span:nth-of-type(1)"
            )
            .get_attribute("textContent")
            .strip()
        )
        city = (
            driver.find_element_by_css_selector(
                "a.campus-address > span:nth-of-type(3)"
            )
            .get_attribute("textContent")
            .split(",")[0]
            .strip()
        )
        state = (
            driver.find_element_by_css_selector(
                "a.campus-address > span:nth-of-type(3)"
            )
            .get_attribute("textContent")
            .split(",")[1]
            .strip()
            .split(" ")[0]
        )
        zip_code = (
            driver.find_element_by_css_selector(
                "a.campus-address > span:nth-of-type(3)"
            )
            .get_attribute("textContent")
            .strip()
            .split(",")[1]
            .strip()[-5:]
        )

        if zip_code == "":
            zip_code = "<MISSING>"

        latitude = (
            driver.find_element_by_css_selector("a.campus-address")
            .get_attribute("href")
            .replace("https://www.google.com/maps/dir//", "")
            .split(",")[0]
        )
        longitude = (
            driver.find_element_by_css_selector("a.campus-address")
            .get_attribute("href")
            .replace("https://www.google.com/maps/dir//", "")
            .split(",")[1]
        )
        phone_number = driver.find_element_by_css_selector(
            "span.campus-tel > a"
        ).get_attribute("textContent")
        hour = driver.find_element_by_css_selector(
            "div.campus-service-times.small-12.small-centered.medium-6.large-12.columns"
        ).get_attribute("textContent")

        # Store data
        locations_titles.append(location_title)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        latitude_list.append(latitude)
        longitude_list.append(longitude)
        phone_numbers.append(phone_number)
        hours.append(hour)

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
        hour,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        latitude_list,
        longitude_list,
        hours,
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
                hour,
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
