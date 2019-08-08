import csv
import re
import time

from geopy.geocoders import Nominatim
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


def parse_info(street_address, city, state):
    to_remove_list = re.findall(
        "(Ste\s[a-zA-Z0-9]+)|(#[a-zA-Z0-9]+)|(Suite\s[a-zA-Z0-9]+)", street_address
    )
    if len(to_remove_list) > 0:
        to_remove = "".join(to_remove_list[0])
        street_address = street_address.replace(to_remove, "")

    geolocator = Nominatim(user_agent="")

    # Get info
    try:
        location = geolocator.geocode(f"{street_address}, {city}, {state}")
    except:
        location = None

    if location is not None:
        longitude = location.longitude
        latitude = location.latitude
        country = location.raw["display_name"].split(",")[-1]
        zip_code = location.raw["display_name"].split(",")[-2]
    else:
        longitude = "<MISSING>"
        latitude = "<MISSING>"
        country = "<MISSING>"
        zip_code = "<MISSING>"

    return longitude, latitude, country, zip_code


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
        "li.menu-item.menu-item-type-post_type.menu-item-object-page.menu-item-1930 > a"
    ).get_attribute("href")
    driver.get(location_url)

    time.sleep(0.5)
    store_urls = [
        store_url.get_attribute("href")
        for store_url in driver.find_elements_by_css_selector(
            "div.col-md-6 > div.google-map-result > a"
        )
    ]

    for store_url in store_urls:
        driver.get(store_url)
        time.sleep(0.5)

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

        longitude, latitude, country, zip_code = parse_info(
            location_dict["street_address"],
            location_dict["city"],
            location_dict["state"],
        )
        # Paste data
        locations_titles.append(location_dict["locations_title"])
        street_addresses.append(location_dict["street_address"])
        phone_numbers.append(location_dict["phone_number"])
        cities.append(location_dict["city"])
        states.append(location_dict["state"])
        zip_codes.append(zip_code)
        longitude_list.append(longitude)
        latitude_list.append(latitude)
        countries.append(country)
        hours.append(location_dict["hour"])

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
