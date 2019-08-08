import csv
import re
import time

from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://beavertails.com"
CHROME_DRIVER_PATH = "chromedriver"
USER_AGENT = "SafeGraph"


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


def parse_info(street_address, city_state_info):
    geolocator = Nominatim(user_agent=USER_AGENT)

    # Get long and lat
    try:
        location = geolocator.geocode(f"{street_address}, {city_state_info}")
    except:
        location = None

    if location is not None:
        location_info = location.raw["display_name"].split(",")

        try:
            city = location_info[-3]
        except:
            city = "<MISSING>"

        try:
            city = location_info[-5]
        except:
            city = "<MISSING>"

        longitude = location.longitude
        latitude = location.latitude
    else:
        city = "<MISSING>"
        state = "<MISSING>"
        longitude = "<MISSING>"
        latitude = "<MISSING>"

    return (city, state, longitude, latitude)


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
    countries = []
    data = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = driver.find_elements_by_css_selector(
        "ul.fullwidth-menu.nav.upwards > li:nth-child(4) > a"
    )[0].get_attribute("href")
    driver.get(store_url)

    # Loading
    time.sleep(2)

    # Get all listings
    listings = driver.find_elements_by_css_selector("div.wpsl-store-location")

    for listing in listings:
        location_title = listing.find_element_by_css_selector("p > strong").text
        street_address = " ".join(
            [
                address.text
                for address in listing.find_elements_by_css_selector(
                    "p > span.wpsl-street"
                )
            ]
        )
        country = listing.find_element_by_css_selector("p > span.wpsl-country").text
        city_state_info = listing.find_element_by_css_selector(
            "p > span:not(.wpsl-country):not(.wpsl-street)"
        ).text

        if country == "Canada":
            zip_code = city_state_info[-7:]
        else:
            zip_code = city_state_info[-5:]

        city, state, longitude, latitude = parse_info(street_address, city_state_info)

        # Hours not always present
        try:
            hour = listing.find_element_by_css_selector("table.wpsl-opening-hours").text
        except:
            hour = "<MISSING>"

        # Phone not always present
        try:
            phone_number = listing.find_element_by_css_selector(
                "p.wpsl-contact-details > span:nth-of-type(1) > span > a:nth-of-type(2)"
            ).get_attribute("textContent")
        except:
            phone_number = "<MISSING>"

        locations_titles.append(location_title)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        phone_numbers.append(phone_number)
        hours.append(hour)
        longitude_list.append(longitude)
        latitude_list.append(latitude)
        countries.append(country)

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
