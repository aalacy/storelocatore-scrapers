import csv

from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


COMPANY_URL = "http://carltoncards.com/"
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


def parse_info(street_address, city, state):
    geolocator = Nominatim(user_agent=USER_AGENT)

    # Get info
    try:
        location = geolocator.geocode(f"{street_address}, {city}, {state}")
    except:
        location = None

    if location is not None:
        longitude = location.longitude
        latitude = location.latitude
    else:
        longitude = "<INACCESSIBLE>"
        latitude = "<INACCESSIBLE>"

    return longitude, latitude


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
    store_info_url = driver.find_elements_by_css_selector("div.store")

    for store in store_info_url:
        store = store.text.split("\n")
        location_title = " ".join(store[:2])
        street_address = store[2]
        city = store[3].split(",")[0]
        phone_number = store[4]
        hour = " ".join(store[5:])

        if len(store[3].split(",")) == 3:
            state = store[3].split(",")[1]
            zip_code = store[3].split(",")[2]
            country = "Canada"
        else:
            state = store[3].split(",")[1].split(" ")[0]
            zip_code = store[3].split(",")[1].split(" ")[1]
            country = "US"

        longitude, latitude = parse_info(street_address, city, state)

        # Store information
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
