import csv
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.choppedleaf.ca"
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
    phone_numbers = []
    countries = []
    hours = []
    longitutudes = []
    latitudes = []
    data = []

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    location_url = driver.find_element_by_css_selector(
        "li.menu-item.menu-item-type-post_type.menu-item-object-page.menu-item-1930 > a"
    ).get_attribute("href")
    driver.get(location_url)

    time.sleep(1)
    store_urls = [
        store_url.get_attribute("href")
        for store_url in driver.find_elements_by_css_selector(
            "div.col-md-6 > div.google-map-result > a"
        )
    ]

    for store_url in store_urls:
        driver.get(store_url)
        time.sleep(1)

        location_dict = {
            "locations_title": "<MISSING>",
            "street_address": "<MISSING>",
            "city": "<MISSING>",
            "state": "<MISSING>",
            "hour": "<MISSING>",
            "phone_number": "<MISSING>",
        }

        location_dict["locations_title"] = driver.find_element_by_css_selector(
            "header > h1"
        ).text

        location_infos = [
            location_info.text
            for location_info in driver.find_elements_by_css_selector(
                "div.row > div.col-sm-6 > div.well > ul.list-unstyled > li"
            )
        ]

        match_string = driver.find_element_by_css_selector(
            "div.google-map-object"
        ).get_attribute("data-data")
        latitude = (
            re.search('("lat":)([-+]?)([\d]{1,3})(((\.)(\d+)()))', match_string)
            .group(0)
            .replace('"lat":', "")
        )
        longitutude = (
            re.search('("lng":)([-+]?)([\d]{1,3})(((\.)(\d+)()))', match_string)
            .group(0)
            .replace('"lng":', "")
        )

        for location_info in location_infos:
            if "Street:" in location_info:
                location_dict["street_address"] = location_info.replace("Street: ", "")
            elif "City:" in location_info:
                location_dict["city"] = location_info.replace("City: ", "")
            elif "Province:" in location_info:
                location_dict["state"] = location_info.replace("Province: ", "")
            elif "Phone:" in location_info:
                location_dict["phone_number"] = location_info.replace("Phone: ", "")
            else:
                location_dict["hour"] = location_info

        if location_dict["state"] == "Washington":
            country = "US"
        else:
            country = "Canada"

        # Paste data
        latitudes.append(latitude)
        longitutudes.append(longitutude)
        locations_titles.append(location_dict["locations_title"])
        street_addresses.append(location_dict["street_address"])
        phone_numbers.append(location_dict["phone_number"])
        cities.append(location_dict["city"])
        states.append(location_dict["state"])
        countries.append(country)
        hours.append(location_dict["hour"])

    # Store data
    for (
        locations_title,
        street_address,
        city,
        state,
        phone_number,
        hour,
        country,
        latitude,
        longitutude,
    ) in zip(
        locations_titles,
        street_addresses,
        cities,
        states,
        phone_numbers,
        hours,
        countries,
        latitudes,
        longitutudes,
    ):
        # Filter out coming soon stores
        if "coming soon" in locations_title.lower():
            pass
        else:
            data.append(
                [
                    COMPANY_URL,
                    locations_title,
                    street_address,
                    city,
                    state,
                    "<MISSING>",
                    country,
                    "<MISSING>",
                    phone_number,
                    "<MISSING>",
                    latitude,
                    longitutude,
                    hour,
                ]
            )

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
