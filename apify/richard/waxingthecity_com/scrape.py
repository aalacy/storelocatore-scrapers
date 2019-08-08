import csv
import time

from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "https://www.waxingthecity.com/"
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


def get_long_lat(address, city, state):
    geolocator = Nominatim(user_agent=USER_AGENT)
    try:
        location = geolocator.geocode(f"{address}, {city}, {state}")
    except:
        location = None

    if location is not None:
        return location.longitude, location.latitude
    else:
        return "<MISSING>", "<MISSING>"


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
        "ul.nav.navbar-nav.navbar-right > li:nth-child(2) > a"
    )[0].get_attribute("href")
    driver.get(store_url)

    # Fetch address/phone elements
    listings = [
        address.text
        for address in driver.find_elements_by_css_selector("div.col-xs-10")
    ]

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

    for listing in listings:
        location_title, address, city, state, zip_code, phone, hour = parse_info(
            listing
        )
        longitude, latitude = get_long_lat(address, city, state)
        locations_titles.append(location_title)
        street_addresses.append(address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        phone_numbers.append(phone)
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
