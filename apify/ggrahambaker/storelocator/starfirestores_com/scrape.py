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

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://starfirestores.com/'
    ext = 'hq-and-locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div#copy')
    stores = main.find_elements_by_css_selector('p')
    all_store_data = []
    for store in stores:
        content = store.text.split('\n')

        if len(content) > 1:
            location_name = content[0]
            if 'Corporate' in location_name:
                location_type = 'Corporate Office'
                addy = content[1].split('.')
                street_address = addy[0]
                city, state, zip_code = addy_ext(addy[1].strip())
                phone_number = content[2].replace('Ph:', '').strip()
                store_number = '<MISSING>'
            else:
                location_name = content[1]
                start_idx = content[0].find('#')
                store_number = content[0][start_idx + 1:].replace(')', '').strip()

                city_state = content[0].split('(')[0].split(',')
                if len(city_state) == 1:
                    city = city_state[0].strip()
                    state = '<MISSING>'
                else:
                    city = city_state[0].strip()
                    state = city_state[1].strip()

                street_address = content[2]
                zip_code = content[3]
                phone_number = content[4]

            lat = '<MISSING>'
            longit = '<MISSING>'

            location_type = '<MISSING>'

            hours = '<MISSING>'
            country_code = 'US'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]

            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
