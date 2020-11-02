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
    locator_domain = 'http://www.hkhonduraskitchen.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    id_list = ['#page-5caff4cb9b747a373a62dd8f', '#page-5caff8c8ee6eb05e9cd85bd3']

    all_store_data = []
    for id_tag in id_list:
        main = driver.find_element_by_css_selector('div' + id_tag)
        content = main.text.split('\n')

        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        hours = content[4] + ' ' + content[5]
        phone_number = content[7]

        map_element = main.find_element_by_css_selector('div.sqs-block.map-block.sqs-block-map')
        json_addy_to = map_element.get_attribute('data-block-json')
        json_addy = json.loads(json_addy_to)

        lat = json_addy['location']['markerLat']
        longit = json_addy['location']['markerLng']

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
