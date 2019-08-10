import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


COMPANY_URL = "https://www.phoenixrehab.com"
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
    latitude_list = []
    longitude_list = []
    data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    location_url = driver.find_element_by_css_selector(
        "li.menu-item.menu-item-type-post_type.menu-item-object-page.menu-item-6426 > a"
    ).get_attribute("href")
    driver.get(location_url)

    # Get listings
    listings = [
        listing.text
        for listing in driver.find_elements_by_css_selector(
            "li.stockist-result.stockist-list-result"
        )
    ]

    listing_urls = [
        url.get_attribute("href")
        for url in driver.find_elements_by_css_selector(
            "div.stockist-result-website > a"
        )
    ]

    for listing in listings:
        listing = [
            listing
            for listing in listing.split("\n")
            if listing
            not in [
                "Physical Therapy",
                "Occupational Health",
                "Athletic Training",
                "VIEW LOCATION PAGE",
                "Occupational Therapy",
                "Athletic Training",
                "Massage Therapy",
                "Pilates",
                "Chiropractic",
            ]
        ]
        locations_title = listing[0]
        phone_number = listing[-1]
        street_address = " ".join(listing[1:-2])
        city = listing[-2].split(",")[0]
        state = listing[-2].split(",")[1].strip().split(" ")[0]
        zip_code = listing[-2].split(",")[1].strip().split(" ")[1]

        locations_titles.append(locations_title)
        street_addresses.append(street_address)
        phone_numbers.append(phone_number)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)

    # Get hours
    for url in listing_urls:
        driver.get(url)

        # Wait until element appears - 10 secs max
        wait = WebDriverWait(driver, 10).until(
            ec.visibility_of_element_located(
                (By.CSS_SELECTOR, ".col-md-7.pr-0.border-line-left")
            )
        )

        hours.append(
            driver.find_element(By.CSS_SELECTOR, ".col-md-7.pr-0.border-line-left").text
        )

        long_lat = re.search(
            "([-+]?)([\d]{1,3})(((\.)(\d+)()))%2C([-+]?)([\d]{1,3})(((\.)(\d+)()))",
            driver.find_element_by_id("page-dynamic-styles").get_attribute(
                "textContent"
            ),
        ).group(0)
        latitude_list.append(long_lat.split("%2C")[0])
        longitude_list.append(long_lat.split("%2C")[1])

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
