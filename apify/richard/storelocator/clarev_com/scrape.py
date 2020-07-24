import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

COMPANY_URL = 'https://www.clarev.com/'
CHROME_DRIVER_PATH = 'chromedriver'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow([
            "locator_domain",
            "page_url",
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


def fetch_data():
    # store data
    locations_titles = []
    street_addresses = []
    cities = []
    states = []
    zip_codes = []
    latitude_list = []
    longitude_list = []
    phone_numbers = []
    hours = []
    data = []

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

    # Fetch store urls from location menu
    location_url = 'https://www.clarev.com/pages/locations'
    driver.get(location_url)

    # Wait until element appears - 10 secs max
    wait = WebDriverWait(driver, 10)
    wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, ".shopify-section.grid.display-flex.page-builder")))


    locations = driver.find_elements_by_css_selector('div.grid__item.large--one-half.medium--one-half.small--one-whole.padding-left')

    for location in locations:
        location_title = location.find_element_by_css_selector('h1.small--text-left').text.strip()
        phone_number = location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left > span > p').get_attribute('textContent').split('\n')[0]
        street_address = location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left > span > p.text-style-capitalize').get_attribute('textContent').split('\n')[0]
        city = location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left > span > p.text-style-capitalize').get_attribute('textContent').split('\n')[1].split(',')[0]
        state = location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left > span > p.text-style-capitalize').get_attribute('textContent').split('\n')[1].split(',')[1].strip().split(' ')[0]
        zip_code = location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left > span > p.text-style-capitalize').get_attribute('textContent').split('\n')[1].split(',')[1].strip().split(' ')[1]
        hour = location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left.text-right > span > p:nth-of-type(2)').get_attribute('textContent').strip()
        if " time" in hour:
        	hour = hour[hour.find(" time")+5:].strip()

        if location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left > h3 > a').get_attribute('href') !=  '':
            latitude = re.search('([-+]?)([\d]{1,3})(((\.)(\d+)())),([-+]?)([\d]{1,3})(((\.)(\d+)()))', location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left > h3 > a').get_attribute('href')).group(0).split(',')[0]
            longitude = re.search('([-+]?)([\d]{1,3})(((\.)(\d+)())),([-+]?)([\d]{1,3})(((\.)(\d+)()))', location.find_element_by_css_selector('div.grid__item.one-half.small--one-whole.small--text-left > h3 > a').get_attribute('href')).group(0).split(',')[1]
        else:
            latitude = '<MISSING>'
            longitude = '<MISSING>'

        # Store data
        locations_titles.append(location_title)
        street_addresses.append(street_address)
        cities.append(city)
        states.append(state)
        zip_codes.append(zip_code)
        latitude_list.append(latitude)
        longitude_list.append(longitude)
        phone_numbers.append(phone_number)
        hours.append(hour)

    # Store data
    for locations_title, street_address, city, state, zipcode, phone_number, latitude, longitude, hour in zip(locations_titles, street_addresses, cities, states, zip_codes, phone_numbers, latitude_list, longitude_list, hours):
        data.append([
            COMPANY_URL,
            location_url,
            locations_title,
            street_address,
            city,
            state,
            zipcode,
            'US',
            '<MISSING>',
            phone_number,
            '<MISSING>',
            latitude,
            longitude,
            hour,
        ])

    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
