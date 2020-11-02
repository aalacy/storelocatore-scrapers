import csv
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


COMPANY_URL = "https://www.phoenixrehab.com"
CHROME_DRIVER_PATH = "chromedriver"

# ZM See if you can abstract out methods like this one 
# in a base class to reuse them
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
    store_numbers = []
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    phone_numbers = []
    latitude_list = []
    longitude_list = []
    data = []
    location_hours = {}

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(
        "https://stockist.co/api/v1/u4291/locations/all.js?callback=_stockistAllStoresCallback"
    )

    # ZM Putting your crawler on sleep to wait for page to return is a 
    # nondeterministic operation. Some sites may take longer than others 
    # to load. I would advise checking for something on the requested
    # website that you expect to find there. Some examples of that would
    # be site name, page title, login link, etc.
    time.sleep(1)

    listings = json.loads(
        driver.find_element_by_css_selector("pre").text.replace(
            "_stockistAllStoresCallback(", ""
        )[:-2]
    )

    for listing in listings:
        store_numbers.append(listing["id"])
        locations_titles.append(listing["name"])
        latitude_list.append(listing["latitude"])
        longitude_list.append(listing["longitude"])
        street_addresses.append(
            listing["address_line_1"] + " " + listing["address_line_2"]
            if listing["address_line_2"]
            else listing["address_line_1"]
        )
        cities.append(listing["city"])
        states.append(listing["state"])
        zip_codes.append(listing["postal_code"])
        phone_numbers.append(listing["phone"])

    url = "https://www.phoenixrehab.com/locations/"
    driver.get(url)

    listing_urls = [
        url.get_attribute("href")
        for url in driver.find_elements_by_css_selector(
            "ul.state-locations-list > li > a"
        )
    ]

    # Get hours
    for url in listing_urls:
        driver.get(url)

        id = (
            driver.find_element_by_css_selector("p.phone > a.phone-link")
            .get_attribute("textContent")
            .strip()
        )
        location_hours[id] = driver.find_element(
            By.CSS_SELECTOR, ".col-md-7.pr-0.border-line-left"
        ).text

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
                location_hours[phone_number],
            ]
        )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
