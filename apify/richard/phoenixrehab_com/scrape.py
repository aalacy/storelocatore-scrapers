import csv
import time
import re
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COMPANY_URL = 'https://www.phoenixrehab.com'
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


def parse_info(street_address, city, state):
    to_remove_list = re.findall('(Ste\s[a-zA-Z0-9]+)|(#[a-zA-Z0-9]+)|(Suite\s[a-zA-Z0-9]+)', street_address)
    if len(to_remove_list) > 0:
        to_remove = ''.join(to_remove_list[0])
        street_address = street_address.replace(to_remove, '')

    geolocator = Nominatim(user_agent="")

    # Get info
    try:
        location = geolocator.geocode(f"{street_address}, {city}, {state}")
    except:
        location = None

    if location is not None:
        longitude = location.longitude
        latitude = location.latitude
        country = location.raw['display_name'].split(',')[-1]
    else:
        longitude = '<MISSING>'
        latitude = '<MISSING>'
        country = '<MISSING>'

    return longitude, latitude, country


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
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    location_url = driver.find_element_by_css_selector('li.menu-item.menu-item-type-post_type.menu-item-object-page.menu-item-6426 > a').get_attribute('href')
    driver.get(location_url)
    time.sleep(2)

    # Get listings
    listings = [listing.text for listing in driver.find_elements_by_css_selector('li.stockist-result.stockist-list-result')]
    listing_urls = [url.get_attribute('href') for url in driver.find_elements_by_css_selector('div.stockist-result-website > a')]

    for listing in listings:
        listing = [listing for listing in listing.split('\n') if listing not in ['Physical Therapy', 'Occupational Health', 'Athletic Training', 'VIEW LOCATION PAGE', 'Occupational Therapy', 'Athletic Training', 'Massage Therapy', 'Pilates', 'Chiropractic']]
        locations_title = listing[0]
        phone_number = listing[-1]
        street_address = ' '.join(listing[1:-2])
        city = listing[-2].split(',')[0]
        state = listing[-2].split(',')[1].strip().split(' ')[0]
        zip_code = listing[-2].split(',')[1].strip().split(' ')[1]
        longitude, latitude, country = parse_info(street_address.split('Suite')[0], city, state)

        locations_titles.append(locations_title)
        street_addresses.append(street_address)
        phone_numbers.append(phone_number)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        longitude_list.append(longitude)
        latitude_list.append(latitude)
        countries.append(country)

    # Get hours
    for url in listing_urls:
        driver.get(url)
        time.sleep(0.5)
        hours.append(driver.find_element_by_class_name('col-md-7.pr-0.border-line-left').text)

    # Store data
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