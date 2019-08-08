import csv
import re
import time

from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.korvette.ca"
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


def parse_info(street_address, city, state):
    to_remove_list = re.findall(
        "(Ste\s[a-zA-Z0-9]+)|(#[a-zA-Z0-9]+)|(Suite\s[a-zA-Z0-9]+)", street_address
    )
    if len(to_remove_list) > 0:
        to_remove = "".join(to_remove_list[0])
        street_address = street_address.replace(to_remove, "")

    geolocator = Nominatim(user_agent="")

    # Only in Canada for now
    country = "CA"

    # Get info
    try:
        location = geolocator.geocode(f"{street_address}, {city}, {state}")
    except:
        location = None

    if location is not None:
        longitude = location.longitude
        latitude = location.latitude
    else:
        longitude = "<INACCESSIBLE>"
        latitude = "<INACCESSIBLE>"

    return longitude, latitude, country


def fetch_data():
    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    longitude_list = []
    latitude_list = []
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
        "ul.nav.navbar-nav.col-lg-9.navbar-divided > li:nth-child(4) > a"
    ).get_attribute("href")
    driver.get(location_url)

    time.sleep(0.5)
    store_urls = [
        url.get_attribute("href")
        for url in driver.find_elements_by_css_selector(
            "div.store__details > h2.h3 > a"
        )
    ]

    for store_url in store_urls:
        driver.get(store_url)
        time.sleep(0.5)
        locations_title = driver.find_element_by_css_selector("header > h1").text
        street_address = " ".join(
            [
                address.text
                for address in driver.find_elements_by_css_selector(
                    "div.row > div:nth-child(1) > p"
                )[:-2]
            ]
        ).strip()
        city = driver.find_elements_by_css_selector("div.row > div:nth-child(1) > p")[
            -2
        ].text.strip()
        state = (
            driver.find_elements_by_css_selector("div.row > div:nth-child(1) > p")[-1]
            .text.strip()[:4]
            .strip()
        )
        zip_code = (
            driver.find_elements_by_css_selector("div.row > div:nth-child(1) > p")[-1]
            .text.strip()[4:]
            .strip()
        )
        phone_number = driver.find_elements_by_css_selector(
            "div.row > div:nth-child(2) > p:nth-child(2)"
        )[0].text.replace("Téléphone : ", "")
        longitude, latitude, country = parse_info(street_address, city, state)
        hour = driver.find_element_by_css_selector(
            "div.row > div:nth-child(3) > p"
        ).text

        # Paste data
        locations_titles.append(locations_title)
        street_addresses.append(street_address)
        phone_numbers.append(phone_number)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        longitude_list.append(longitude)
        latitude_list.append(latitude)
        countries.append(country)
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
        country,
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
