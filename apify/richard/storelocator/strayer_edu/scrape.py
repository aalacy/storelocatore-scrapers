import csv
import json
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.strayer.edu"
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
    hours = []
    longitude_list = []
    latitude_list = []
    data = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = "https://www.strayer.edu/bin/strayer/campuslocations.json"
    driver.get(store_url)

    locations = json.loads(driver.find_element_by_css_selector("pre").text)

    for location in locations:

        # Title
        locations_titles.append(location["jcr:title"])

        # Street address
        street_addresses.append(location["fieldCampusAddress"])

        # City
        cities.append(location["fieldCampusCity"])

        # State
        states.append(location["fieldCampusStateName"])

        # Zip
        zip_codes.append(
            location["fieldCampusZip"]
            if re.match("\d{5}$", location["fieldCampusZip"])
            else "<MISSING>"
        )

        # Phone
        phone_numbers.append(location["fieldCampusPhoneNumber"])

        # Lat
        latitude_list.append(location["fieldCampusLatitude"])

        # Longitude
        longitude_list.append(location["fieldCampusLongitude"])

        # Hour
        hours.append(location["fieldCampusHours"])

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
