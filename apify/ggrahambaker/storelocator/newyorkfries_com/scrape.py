import csv
import os
from sgselenium import SgSelenium
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.newyorkfries.com/'
    ext = 'locations/all'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.execute_script('return canadaEntries;')

    all_store_data = []
    for loc in locs:
        street_address = loc['address']
        if street_address == '':
            street_address = '<MISSING>'
        city = loc['city']
        country_code = 'CA'
        lat = loc['latitude']
        longit = loc['longitude']
        location_name = loc['title']
        state = loc['province']

        hours = '<MISSING>'
        zip_code = '<MISSING>'

        store_number = loc['store_number']
        if store_number == '':
            store_number = '<MISSING>'
        location_type = '<MISSING>'
        phone_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
