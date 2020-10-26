import csv
import os
from sgselenium import SgSelenium
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cottonon_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://cottonon.com/'
    ext = 'AU/store-finder/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    driver.find_element_by_xpath("//option[@value='US']").click()
    element = driver.find_element_by_css_selector('button#dwfrm_storelocator_findByText')
    driver.execute_script("arguments[0].click();", element)

    driver.implicitly_wait(10)
    i = 0
    while i < 32:
        driver.implicitly_wait(10)
        # logger.info(driver.find_element_by_css_selector('button.store-results-load-more').value_of_css_property('display'))
        element = driver.find_element_by_css_selector('button.store-results-load-more')
        driver.execute_script("arguments[0].click();", element)
        i += 1

    stores = driver.find_elements_by_css_selector('div.store-details')
    all_store_data = []
    for store in stores:
        # logger.info(store.get_attribute('data-store'))
        store_json = json.loads(store.get_attribute('data-store'))
        # logger.info(store_json['name'])
        location_name = store_json['name']
        street_address = store_json['address1']
        city = store_json['city']
        state = '<MISSING>'
        zip_code = store_json['postal']
        lat = store_json['lat']
        longit = store_json['lng']
        country_code = 'US'

        phone_number = store.find_element_by_css_selector('div.store-phone').text.replace('Phone:', '').strip()
        if phone_number == '':
            phone_number = '<MISSING>'

        ## get hours
        element = store.find_element_by_css_selector('div.store-more-details')
        driver.execute_script("arguments[0].click();", element)
        driver.implicitly_wait(10)

        hour_div = store.find_element_by_css_selector('div.opening-hours')

        # logger.info(hour_div.text.replace('Opening hours:', '').strip().split('\n'))
        hours = ''
        hour_arr = hour_div.text.replace('Opening hours:', '').strip().split('\n')
        for h in hour_arr:
            if '(Today)' in h:
                hours += h.replace('(Today)', '') + ' '
            else:
                hours += h + ' '

        hours = hours.strip()

        location_type = '<MISSING>'
        phone_number = '<MISSING>'
        store_number = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
