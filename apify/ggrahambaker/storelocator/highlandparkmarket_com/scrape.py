import csv
import os
from sgselenium import SgSelenium
import json

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
    locator_domain = 'https://www.highlandparkmarket.com/contact'
    ext = 'contact'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    stores = driver.find_elements_by_css_selector('div.row.sqs-row')
    del stores[8]
    del stores[7]
    del stores[6]
    del stores[2]
    del stores[0]
    all_store_data = []
    for store in stores:
        content = store.text.split('\n')
        if len(content) == 10:
            location_name = content[0]
            street_address = content[1]
            city, state, zip_code = addy_ext(content[2])
            hours = content[5] + ' ' + content[6]
            phone_number = content[7].replace('Telephone:', '').strip()
            coords = store.find_element_by_css_selector('div.sqs-block.map-block.sqs-block-map').get_attribute(
                'data-block-json')
            j_coords = json.loads(coords)

            lat = j_coords['location']['markerLat']
            longit = j_coords['location']['markerLng']

            country_code = 'US'

            store_number = '<MISSING>'
            location_type = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
