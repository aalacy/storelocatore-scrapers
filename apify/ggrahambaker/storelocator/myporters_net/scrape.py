import csv
import os
from sgselenium import SgSelenium
import re

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://shop.myporters.net/'
    ext = 'find-your-store/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    driver.implicitly_wait(20)

    locs = driver.find_elements_by_css_selector('tr.location')
    all_store_data = []
    for loc in locs:
        line_arr = loc.text.split('\n')
        location_name = line_arr[0]
        street_address = line_arr[0]
        city, state, zip_code = addy_ext(line_arr[1])
        phone_number = line_arr[2].replace('Phone:', '').strip()
        if phone_number == '':
            phone_number = '<MISSING>'

        hours = line_arr[3].replace('Hours: ', '')
        if 'Ken Houston' in hours:
            hours = line_arr[4].replace('Hours: ', '')
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<INACCESSIBLE>'
        longit = '<INACCESSIBLE>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
