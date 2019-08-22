import csv
import json
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.beggarspizza.com"
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
    location_id = []
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

    store_url = "https://www.beggarspizza.com/locations/"
    driver.get(store_url)
    names = [
        name.get_attribute("textContent")
        for name in driver.find_elements_by_css_selector(
            "div.wpsl-store-location > p > strong > a"
        )
    ]
    urls = [
        url.get_attribute("href")
        for url in driver.find_elements_by_css_selector(
            "div.wpsl-store-location > p > strong > a"
        )
    ]
    hour_dict = {}
    for name, url in zip(names, urls):
        driver.get(url)
        hour = driver.find_element_by_css_selector(
            "div.col-sm-12.reset-left > div.col-xs-6.smallWide.reset-left"
        ).get_attribute("textContent")
        hour_dict[name.strip()] = hour

    # Fetch store urls from location menu
    store_url = "https://www.beggarspizza.com/wp-admin/admin-ajax.php?action=store_search&lat=41.878114&lng=-87.629798&max_results=25&search_radius=1000&autoload=1"
    driver.get(store_url)

    locations = json.loads(driver.find_element_by_css_selector("pre").text)

    for location in locations:
        # ID
        location_id.append(location["id"])

        # Title
        locations_titles.append(location["store"])

        # Street address
        street_addresses.append(location["address"] + " " + location["address2"])

        # City
        cities.append(location["city"])

        # State
        states.append(location["state"])

        # Phone
        phone_numbers.append(location["phone"])

        # Zip
        zip_codes.append(location["zip"])

        # Latitude
        latitude_list.append(location["lat"])

        # Longitude
        longitude_list.append(location["lng"])

        # Hour  - Use backup to reference
        hour = " ".join(re.sub("<[^>]*>", ",", location["hours"]).split(","))
        if hour == "":
            if location["store"] in hour_dict.keys():
                hour = hour_dict[location["store"]]
            else:
                hour = "<MISSING>"
        hours.append(hour)

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
        id,
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
        location_id,
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
                id,
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
