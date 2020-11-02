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
    locator_domain = 'https://www.fritouchickenpizza.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)
    driver.implicitly_wait(10)

    all_store_data = []
    loc = driver.find_element_by_css_selector('div#SITE_FOOTERinlineContent-gridContainer')

    cont = loc.text.split('\n')
    street_address = cont[2].strip()
    addy = cont[3].split(',')
    city = addy[0]
    state = addy[1].strip()
    zip_code = '<MISSING>'
    phone_number = cont[6]
    hours = cont[9] + ' ' + cont[10]

    store_number = '<MISSING>'
    location_type = '<MISSING>'
    location_name = '<MISSING>'

    country_code = 'CA'
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
