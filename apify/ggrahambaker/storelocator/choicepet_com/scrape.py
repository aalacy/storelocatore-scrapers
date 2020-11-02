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
    locator_domain = 'https://choicepet.com/'
    ext = 'pages/locations-1'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    heads = ['headingOne', 'headingTwo', 'headingThree']

    for head in heads:
        div = driver.find_element_by_css_selector('div#' + head)
        element = div.find_element_by_css_selector('button')
        driver.execute_script("arguments[0].click();", element)

    all_store_data = []
    divs = driver.find_elements_by_css_selector('div.card')
    for div in divs:
        stores = div.find_elements_by_css_selector('div.col-md-6')
        for store in stores:
            text_arr = store.text.split('\n')

            if len(text_arr) == 9:
                map_link = store.find_element_by_css_selector('a').get_attribute('href')
                start_idx = map_link.find('r//')
                end_idx = map_link.find('/@')

                coords = map_link[start_idx + 3:end_idx].split(',')
                lat = coords[0]
                longit = coords[1]

                location_name = text_arr[0]
                address = text_arr[1].split(',')
                street_address = address[0]
                city = address[1]
                state_zip = text_arr[2].split(',')[0].split(' ')
                state = state_zip[0]
                zip_code = state_zip[1]
                hours = text_arr[4] + ' ' + text_arr[5]
                phone_number = text_arr[6]

                store_number = '<MISSING>'
                location_type = '<MISSING>'
                country_code = '<MISSING>'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
