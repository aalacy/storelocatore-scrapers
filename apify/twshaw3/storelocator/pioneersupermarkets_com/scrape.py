import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_location(location):
    return [
        'pioneersupermarkets.com',
        location['name'],
        location['address1'],
        location['city'],
        location['state'],
        location['zipCode'],
        'US',
        location['storeNumber'],
        location['phone'],
        '<MISSING>',
        location['latitude'],
        location['longitude'],
        location.get('hourInfo', '<MISSING>').strip().replace('\n', ', ')
    ]

def fetch_data():
    driver = get_driver()

    driver.get('https://pioneersupermarkets.com/locations')

    locations = driver.execute_script("return S.mapManager.locations")

    data = [parse_location(location) for location in locations]

    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
