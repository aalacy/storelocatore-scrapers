import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

#helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    return city, state, zip_code

def fetch_data():
    data = []
    driver = SgSelenium().chrome()

    locator_domain = 'https://www.primohoagies.com/'
    ext = 'find-a-primo.php'
    driver.get(locator_domain + ext)
    store_name = driver.find_element_by_css_selector('ul#locations-list')
    lis = store_name.find_elements_by_css_selector('li')

    all_store_data = []
    for store in lis:
        location_name = store.find_element_by_css_selector('span.list-location-title').text
        street_address = store.find_element_by_css_selector('span.list-location-address').text
        city_state = store.find_element_by_css_selector('span.list-location-city-state').text
        city, state, zip_code = addy_extractor(city_state)

        phone_number = store.find_element_by_css_selector('span.list-location-phone').text

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = '<INACCESSIBLE>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)

    # End scraper

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
