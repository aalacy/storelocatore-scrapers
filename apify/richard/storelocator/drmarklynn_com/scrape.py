import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://drmarklynn.com/"
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


def parse_info(item):
    item = item.split("\n")
    location_title = item[0]
    address = item[1]
    hours = "<MISSING>"
    phone = item[3]
    city = item[2].split(",")[0]
    state = item[2].split(",")[1].strip().split(" ")[0]
    zip_code = item[2].split(",")[1].strip().split(" ")[1]

    return location_title, address, city, state, zip_code, phone, hours


def fetch_data():
    data = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = driver.find_elements_by_css_selector(
        "ul.menu.fl-menu-horizontal.fl-toggle-arrows > li:nth-child(3) > a"
    )[0].get_attribute("href")
    driver.get(store_url)

    # Loading
    time.sleep(5)

    # Get all listings
    listings = [
        address.text
        for address in driver.find_elements_by_css_selector("div.address-text-wrap")
    ]

    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    hours = []

    for listing in listings:
        location_title, address, city, state, zip_code, phone, hour = parse_info(
            listing
        )
        locations_titles.append(location_title)
        street_addresses.append(address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        phone_numbers.append(phone)
        hours.append(hour)

    for (
        locations_title,
        street_address,
        city,
        state,
        zipcode,
        phone_number,
        hour,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        zip_codes,
        phone_numbers,
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
