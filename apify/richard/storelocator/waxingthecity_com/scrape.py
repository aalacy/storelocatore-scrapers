import csv
import re

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


COMPANY_URL = "https://www.waxingthecity.com/"
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
    hours = item[-2].replace("Closed Now", "")
    phone = item[-4]
    city = item[-5].split(",")[0]
    state = item[-5].split(",")[1].strip().split(" ")[0]
    zip_code = item[-5].split(",")[1].strip().split(" ")[1]
    if len(item) == 7:
        address = item[1]
    else:
        address = item[1] + " " + item[2]

    return location_title, address, city, state, zip_code, phone, hours


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
    store_url = "https://studios.waxingthecity.com"
    driver.get(store_url)

    # Wait till the element loads
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located(
            (By.CSS_SELECTOR, ".push-top.clearfix.store-buttons")
        )
    )

    # listings = driver.find_elements_by_css_selector('div.col-sm-4 > a')
    listing_urls = [
        listing.get_attribute("href")
        for listing in driver.find_elements_by_css_selector(
            "div.push-top.clearfix.store-buttons > a:nth-of-type(1)"
        )
    ]

    # Go through each listing and append data
    for listing_url in listing_urls:
        driver.get(listing_url)

        location_title = driver.find_element_by_css_selector(
            "h1.no-margin.ng-binding"
        ).text
        street_address = driver.find_element_by_css_selector(
            "div.no-bold.line-height-bump > p"
        ).text
        city = driver.find_element_by_css_selector(
            "div.no-bold.line-height-bump > span:nth-of-type(1)"
        ).text
        state = driver.find_element_by_css_selector(
            "div.no-bold.line-height-bump > span:nth-of-type(2)"
        ).text
        zip_code = driver.find_element_by_css_selector(
            "div.no-bold.line-height-bump > span:nth-of-type(3)"
        ).text
        phone_number = driver.find_element_by_css_selector(
            "div.hidden-xs.tel-number.ng-binding"
        ).text
        hour = driver.find_element_by_css_selector(
            "div.hours-card.ng-isolate-scope > div.ng-scope"
        ).text
        long_lat = driver.find_element_by_css_selector(
            "div.map-container.push-bottom.ng-isolate-scope > img"
        ).get_attribute("data-at2x")
        long_lat_list = (
            re.search(
                "[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)",
                long_lat,
            )
            .group(0)
            .split(",")
        )
        longitude = long_lat_list[0]
        latitude = long_lat_list[1]

        locations_titles.append(location_title)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        phone_numbers.append(phone_number)
        hours.append(hour)
        longitude_list.append(longitude)
        latitude_list.append(latitude)

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
