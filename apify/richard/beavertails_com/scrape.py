import csv
import re
import time
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COMPANY_URL = 'https://beavertails.com'
CHROME_DRIVER_PATH = './chromedriver'
USER_AGENT = 'SafeGraph'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow([
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
            "hours_of_operation"
        ])
        # Body
        for row in data:
            writer.writerow(row)


def parse_info(store):
    geolocator = Nominatim(user_agent = USER_AGENT)
    store = store.replace('Email Us', '').replace('Visit us on Facebook', '').replace('Find on map', '')
    store = [store_info for store_info in store.split('\n') if store_info != '']
    location_title = store[0]
    address = store[1]
    country = store[3]

    # Get phone
    if re.match('(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', store[-1]):
        phone = store[-1]
        hour = '\n'.join(store[4:-1])
    else:
        phone = '<MISSING>'
        hour = '\n'.join(store[4:])

    # Get long and lat
    try:
        location = geolocator.geocode(f"{address}, {store[2]}")
    except:
        location = None

    if location is not None:
        location_info = location.raw['display_name'].split(',')
        city = location_info[3]
        state = location_info[-3]
        longitude = location.longitude
        latitude = location.latitude
        zip_code = location_info[-2]
    else:
        city = '<MISSING>'
        state = '<MISSING>'
        longitude = '<MISSING>'
        latitude = '<MISSING>'
        zip_code = '<MISSING>'

    return location_title, address, city, state, zip_code, phone, hour, longitude, latitude, country


def fetch_data():
    data = []
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = driver.find_elements_by_css_selector('ul.fullwidth-menu.nav.upwards > li:nth-child(4) > a')[0].get_attribute('href')
    driver.get(store_url)

    # Loading
    time.sleep(5)

    # Get all listings
    listings = [address.text for address in driver.find_elements_by_css_selector('div.wpsl-store-location')]

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

    for listing in listings:
        location_title, address, city, state, zip_code, phone, hour, longitude, latitude, country = parse_info(listing)
        locations_titles.append(location_title)
        street_addresses.append(address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        phone_numbers.append(phone)
        hours.append(hour)
        longitude_list.append(longitude)
        latitude_list.append(latitude)
        countries.append(country)

    for locations_title, street_address, city, state, zipcode, phone_number, latitude, longitude, hour, country in zip(locations_titles, street_addresses, cities, states, zip_codes, phone_numbers, latitude_list, longitude_list, hours, countries):
        data.append([
            COMPANY_URL,
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phone_number,
            '<MISSING>',
            latitude,
            longitude,
            hour
        ])

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()



