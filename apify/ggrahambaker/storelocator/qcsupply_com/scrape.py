import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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
    driver = SgSelenium().chrome()
    locator_domain = 'https://www.qcsupply.com/'
    ext = 'locations/'

    driver.get(locator_domain + ext)
    all_store_data = []

    wrapper = driver.find_element_by_css_selector('div#amlocator_left')
    spans = wrapper.find_elements_by_name('leftLocation')

    for span in spans:
        split_cont = span.text.split('\n')
        location_name = split_cont[0]
        street_address = split_cont[1]
        city, state, zip_code = addy_extractor(split_cont[2])
        phone_number = split_cont[3].replace('Phone: ', '')
        
        if '/' in phone_number:
            phone_number = phone_number.split('/')[0].strip()

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = '<INACCESSIBLE>'
        lat = '<INACCESSIBLE>'
        longit = '<INACCESSIBLE>'

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
