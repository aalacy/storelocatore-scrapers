import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://fruthpharmacy.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)
    time.sleep(2)

    select = Select(driver.find_element_by_id('radiusSelect'))
    select.select_by_value('500')
    time.sleep(2)

    states = ['Kentucky', 'virginia', 'west virginia']
    all_store_data = []
    dup_tracker = set()
    for state in states:

        addy_input = driver.find_element_by_css_selector('input#addressInput')
        addy_input.send_keys(state)

        driver.find_element_by_id('addressSubmit').click()

        time.sleep(2)

        main = driver.find_element_by_css_selector('div#map_sidebar')
        locs = main.find_elements_by_css_selector('div.results_entry')

        for loc in locs:

            location_name = loc.find_element_by_css_selector('span.location_name').text
            if location_name not in dup_tracker:
                dup_tracker.add(location_name)
            else:
                continue

            store_number = location_name.split('#')[1].strip()
            street_address = loc.find_element_by_css_selector('span.slp_result_address.slp_result_street').text
            address = loc.find_element_by_css_selector('span.slp_result_address.slp_result_citystatezip').text.split(',')

            city = address[0]
            state = address[1].strip()
            if len(state.split(' ')) == 2:
                state_zip = state.split(' ')
                state = state_zip[0]
                if state_zip[1].isdigit():
                    zip_code = state_zip[1]
                else:
                    state += ' ' + state_zip[1]
                
                zip_code == '<MISSING>'
            elif len(state.split(' ')) == 3:
                state_zip = state.split(' ')
                state = state_zip[0] + ' ' + state_zip[1]
                zip_code = state_zip[2]

            else:
                zip_code = '<MISSING>'

            phone_number = loc.find_element_by_css_selector('span.slp_result_address.slp_result_phone').text
            if phone_number == '':
                phone_number = '<MISSING>'

            hours = loc.find_element_by_css_selector('span.slp_result_hours').text.replace('\n', ' ').split('Need a prescription')[0]
            hours =  hours.replace('Store Hours:', '').strip()
            country_code = 'US'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            page_url = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
