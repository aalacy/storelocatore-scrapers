import csv
import os
from geopy.geocoders import Nominatim
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COMPANY_URL = 'https://www.pastosa.com/'

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


def parse_address(driver):
    addresses = [address.text for address in driver.find_elements_by_css_selector('div.locations-row__info-details.locations-row__info-details--address')]
    street_address = []
    city = []
    state = []
    zip = []

    for address in addresses:
        address_split = address.split('\n')
        street_address.append(address_split[0])
        zip.append(address_split[1][-5:])
        city.append(address_split[1][:-6].split(',')[0])
        state.append(address_split[1][:-6].split(',')[1].strip())

    return street_address, city, state, zip

def parse_hours(driver):
    hours_list = driver.find_elements_by_css_selector('div.col-xs-6.col-sm-12.col-lg-6.no-pad-right-xs.no-pad-right-lg')
    hours_str = ''
    for hour in hours_list:
        hours_str += hour.text
    hours = [hour.lstrip() for hour in hours_str.replace('\n', ' ').split('Hours')[1:]]
    return hours

def parse_phone(driver):
    phone = []
    phone_list = driver.find_elements_by_css_selector('div.col-xs-6.col-sm-12.col-lg-6.no-pad-left-xs.no-pad-left-lg')
    phone_str = ''
    for phone in phone_list:
        phone_str += phone.text
    phone = [phone.lstrip() for phone in phone_str.replace('\n', ' ').split('Phone')[1:]]
    return phone

def get_long_lat(address, city, state):
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    try:
        location = geolocator.geocode(f"{address}, {city}, {state}")
    except:
        location = ''

    if location is not None:
        return location.longitude, location.latitude
    else:
        return '<MISSING>', '<MISSING>'


def fetch_data():
    data = []
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.get(COMPANY_URL)

    # Fetch store urls from location menu
    store_url = driver.find_elements_by_css_selector('ul.vnav.vnav--horizontal > li:nth-child(8) > a')[0].get_attribute('href')
    driver.get(store_url)

    # Fetch address/phone elements
    locations_titles = [titles.text for titles in driver.find_elements_by_css_selector('h2.locations-row__title')]
    locations_subtitles = [subtitle.text for subtitle in driver.find_elements_by_css_selector('p.locations-row__subtitle')]
    street_addresses, cities, states, zip_codes = parse_address(driver)
    hours = parse_hours(driver)
    phone_numbers = parse_phone(driver)

    # Get longitude and latitude
    longitude_list = []
    latitude_list = []
    for street_address, city, state in zip(street_addresses, cities, states):
        longitude, latitude = get_long_lat(street_address, city, state)
        longitude_list.append(longitude)
        latitude_list.append(latitude)

    data = []
    for locations_title, locations_subtitle, street_address, hour, city, state, zipcode, phone_number, latitude, longitude, hour in zip(locations_titles, locations_subtitles, street_addresses, hours, cities, states, zip_codes, phone_numbers, latitude_list, longitude_list, hours):
        data.append([
            COMPANY_URL,
            locations_title + ' ' + locations_subtitle,
            street_address,
            city,
            state,
            zip,
            'US',
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