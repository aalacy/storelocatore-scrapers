import csv
import os
from sgselenium import SgSelenium
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://minutemanfoodmart.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []
    body = driver.find_element_by_css_selector('tbody.row-hover')
    stores = body.find_elements_by_css_selector('tr')
    for store in stores:
        info = store.text.split('\n')
        location_name = info[0]
        pound_idx = info[0].find('#')
        store_number = info[0][pound_idx + 1:]

        ## address. logic
        add_split = info[1].split(',')
        street_address = add_split[0]
        city = add_split[1]
        state_zip = add_split[2].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]

        phone_number = info[2].replace('Phone: ', '')

        href = store.find_elements_by_css_selector('a')[1].get_attribute('href')
        start_idx = href.find('/@')
        end_idx = href.find('z/da')
        coords = href[start_idx + 2:end_idx].split(',')
        lat = coords[0]
        longit = coords[1]

        country_code = 'US'
        location_type = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
