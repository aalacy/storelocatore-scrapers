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

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    if len(state_zip) == 2:
        zip_code = state_zip[0] + ' ' + state_zip[1]
        state = '<MISSING>'
    else:
        zip_code = state_zip[1] + ' ' + state_zip[2]
        state = state_zip[0]

    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://west49.com/'
    ext = 'pages/store-locator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    element = driver.find_element_by_css_selector('button.language-popup__btn')
    driver.execute_script("arguments[0].click();", element)
    select = driver.find_element_by_css_selector('select.store__pagination-dropdown.js-pagination-dropdown')

    options = select.find_elements_by_css_selector('option')

    all_store_data = []
    switch = False
    for opt in options:
        opt.click()
        time.sleep(1)
        stores = driver.find_elements_by_css_selector('div.store__list')
        for store in stores:

            cont = store.text.split('\n')

            location_type = cont[0]
            location_name = cont[1]
            street_address = cont[2]
            if 'Unit' in cont[3]:
                street_address += ' ' + cont[4]
                off = 1
            else:
                off = 0

            city, state, zip_code = addy_ext(cont[3 + off])

            hours = ''
            for h in cont[5 + off:]:
                hours += h + ' '

            if 'Trois Rivieres' in location_name:
                if not switch:
                    switch = True
                else:
                    continue

            store_number = '<MISSING>'

            country_code = 'CA'
            lat = '<MISSING>'
            longit = '<MISSING>'
            phone_number = store.find_element_by_css_selector('div.store__list-phone').text

            if phone_number == '':
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
