import csv
import re
import time
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COMPANY_URL = 'https://www.pridestaff.com'
CHROME_DRIVER_PATH = './chromedriver'

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


def parse_info(address):
    geolocator = Nominatim(user_agent = USER_AGENT)

    # Get info
    try:
        location = geolocator.geocode(address)
    except:
        location = None

    if location is not None:
        longitude = location.longitude
        latitude = location.latitude
    else:
        longitude = '<MISSING>'
        latitude = '<MISSING>'

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
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = driver.find_elements_by_css_selector('nav.site-nav > ul.ml-0.mb-0 > li:nth-child(3) > a')[0].get_attribute('href')
    driver.get(store_url)

    # Loading
    time.sleep(2)

    # Get all locations url
    listing_urls = [listing_url.get_attribute('href') for listing_url in driver.find_elements_by_css_selector('div.row.row-cell--third.locations > div > ul.noaftermath > li > a')]

    for listing_url in listing_urls:
        driver.get(listing_url)
        time.sleep(1)

        # Extract location information
        location_title = driver.find_element_by_class_name('h2.center').text
        address_info = [location_info.text for location_info in driver.find_elements_by_css_selector('ul.location-address.noaftermath > li')]
        if address_info[0] == 'Coming Soon':
            street_address = '<MISSING>'
        else:
            street_address = ' '.join(address_info[:-1])
        city = address_info[-1].split(',')[0]
        state = address_info[-1].split(',')[1].split(' ')[0]
        zip_code = address_info[-1].split(',')[1].split(' ')[1]
        longitude, latitude = parse_info(address_info[0] + ' ' + address_info[-1])
        try:
            phone_number = driver.find_element_by_css_selector('ul.location-contact > li:nth-child(1) > a').text
        except:
            phone_number = '<MISSING>'

        # Store information
        locations_titles.append(location_title)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        phone_numbers.append(phone_number)
        hours.append('<MISSING>')
        longitude_list.append(longitude)
        latitude_list.append(latitude)
        countries.append('US')

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


