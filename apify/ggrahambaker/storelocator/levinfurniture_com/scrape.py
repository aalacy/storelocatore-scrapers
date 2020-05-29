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

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.levinfurniture.com/'
    ext = 'store/locator/show-all-locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    stores = driver.find_elements_by_css_selector('div.store-locator-stores-result-list-item.au-store-locator-stores-result-list-item')

    all_store_data = []
    for store in stores:
        details = store.text.split('\n')

        location_name = details[0]
        street_address = details[1]
        city, state, zip_code = addy_ext(details[2])

        phone_number = details[3]
        hours = ''
        for h in details[7:]:
            hours += h + ' '

        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
