import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://nambeinternational.com/'
    ext = 'contact-us/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []
    location = driver.find_element_by_css_selector('div.panel-body')

    cont = location.text.split('\n')
    street_address = cont[1] + ' ' + cont[2]
    city = cont[3].replace(',', '')
    state_zip = cont[4].split(' ')
    state = state_zip[0]
    zip_code = state_zip[1].replace(',', '')

    phone_number = cont[-1]
    location_name = cont[0]

    country_code = 'US'
    store_number = '<MISSING>'
    lat = '<MISSING>'
    longit = '<MISSING>'
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
