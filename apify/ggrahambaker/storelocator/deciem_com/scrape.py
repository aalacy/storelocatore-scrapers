import csv
import os
from sgselenium import SgSelenium
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def state_zip_parser(country_code, state_zip):
    if country_code == 'US':
        if len(state_zip) == 3:
            state = state_zip[0] + ' ' + state_zip[1]
            zip_code = state_zip[2]
        else:
            state = state_zip[0] 
            zip_code = state_zip[1]
            
    else:
        if len(state_zip) == 3:
            state = state_zip[0] 
            zip_code = state_zip[1] + ' ' + state_zip[2]
        else:
            state = state_zip[0] + ' ' + state_zip[1]
            zip_code = state_zip[2] + ' ' + state_zip[3]
            
    return state, zip_code

def fetch_data():
    locator_domain = 'https://deciem.com/'
    ext = 'find-us'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('div.location-name-container')

    all_store_data = []
    dup_tracker = set()
    for loc in locs:
        country_name = loc.find_element_by_xpath('..').find_element_by_css_selector('div.address').find_elements_by_css_selector('span')[-1].get_attribute('innerHTML')##
        
        if country_name != 'Canada' and country_name != 'USA':
            continue
        if country_name == 'Canada':
            country_code = 'CA'
        if country_name == 'USA':
            country_code = 'US'
        
        location_span = loc.find_element_by_css_selector('span.location-name')
        on_click = location_span.get_attribute('onclick')
        location_name = location_span.get_attribute('innerHTML')
        if location_name not in dup_tracker:
            dup_tracker.add(location_name)
        else:
            continue
        
        driver.execute_script(on_click)
        driver.implicitly_wait(5)
        
        addy = driver.find_element_by_css_selector('div.address').text.split('\n')
        if len(addy) == 3:
            street_address = addy[0]
            ect_addy = addy[1].split(',')
            city = ect_addy[0]
            state_zip = ect_addy[1].strip().split(' ')
            
            state, zip_code = state_zip_parser(country_code, state_zip)
            
        else:
            street_address = addy[0] + ' ' + addy[1]
            ect_addy = addy[2].split(',')
            city = ect_addy[0]
            state_zip = ect_addy[1].strip().split(' ')
            
            state, zip_code = state_zip_parser(country_code, state_zip)
            
        phone_number = driver.find_element_by_css_selector('div.tele-container').text.replace('TELEPHONE', '').replace('+1-', '').strip()
        
        hours = driver.find_element_by_css_selector('div.hours-container').text.replace('\n', ' ').replace('HOURS', '').strip()

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        
        time.sleep(2)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
