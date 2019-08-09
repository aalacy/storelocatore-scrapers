import csv
import re
import time

from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.saje.com"
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
    countries = []
    hours = []
    data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    location_url = driver.find_element_by_css_selector(
        "div.store-locator-nav > a"
    ).get_attribute("href")

    driver.get(location_url)
    time.sleep(2)

    locations_titles = [
        location_title.get_attribute("text")
        for location_title in driver.find_elements_by_css_selector(
            "td.store-location-name > a"
        )
    ]
    street_addresses = [
        street_address.get_attribute("textContent")
        for street_address in driver.find_elements_by_css_selector(
            "td.store-location-address > p:nth-child(1)"
        )
    ]
    cities = [
        city_state_info.get_attribute("textContent").split(",")[0]
        for city_state_info in driver.find_elements_by_css_selector(
            "td.store-location-address > p:nth-child(2)"
        )
    ]
    states = [
        city_state_info.get_attribute("textContent").split(",")[1]
        for city_state_info in driver.find_elements_by_css_selector(
            "td.store-location-address > p:nth-child(2)"
        )
    ]
    zip_codes = [
        city_state_info.get_attribute("textContent").split(",")[2]
        for city_state_info in driver.find_elements_by_css_selector(
            "td.store-location-address > p:nth-child(2)"
        )
    ]
    phone_numbers = [
        phone_number.get_attribute("textContent")
        for phone_number in driver.find_elements_by_css_selector(
            "td.store-location-address > p:nth-child(3)"
        )
    ]

    for zip_code in zip_codes:
        if re.match("[A-Z][0-9][A-Z]\s[0-9][A-Z][0-9]", zip_code):
            countries.append("CA")
        else:
            countries.append("US")

    # This is needed to get hours
    store_location_urls = [
        url.get_attribute("href")
        for url in driver.find_elements_by_css_selector(
            "div.googlemap-maindiv > a:nth-child(2)"
        )
    ]

    # Get hours
    for store_location_url in store_location_urls:
        driver.get(store_location_url)
        time.sleep(1)
        hours.append(
            driver.find_element_by_css_selector("div.store-days-hours-detail").text
        )

    for (
        locations_title,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        hour,
        country,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
        hours,
        countries,
    ):
        data.append(
            [
                COMPANY_URL,
                locations_title,
                street_address,
                city,
                state,
                zipcode,
                country,
                "<MISSING>",
                phone_number,
                "<MISSING>",
                "<MISSING>",
                "<MISSING>",
                hour,
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
