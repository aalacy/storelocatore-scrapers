import csv
import os
from sgselenium import SgSelenium
import time

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.firehousesubs.com/'
    ext = 'all-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    states = driver.find_element_by_css_selector('ul.state_list').find_elements_by_css_selector('li')

    state_list = []
    for state in states:
        state_link = state.find_element_by_css_selector('a').get_attribute('href')
        state_list.append(state_link)

    link_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        locs = driver.find_element_by_css_selector('section.locations_wrap').find_elements_by_css_selector('article')
        for loc in locs:
            link = loc.find_element_by_css_selector('a').get_attribute('href')
            link_list.append(link)

    all_store_data = []
    for i, link in enumerate(link_list):
        driver.get(link)
        time.sleep(2)
        driver.implicitly_wait(60)

        loc_info = driver.find_element_by_css_selector('h1').text.split('#')
        if len(loc_info) == 1:
            location_name = loc_info[0].strip()
            store_number = '<MISSING>'
        else:
            location_name = loc_info[0].strip()
            store_number = loc_info[1].strip()

        if 'Coming' in store_number:
            continue

        addy = driver.find_element_by_css_selector('address').text.split('\n')
        if len(addy) == 2:
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1])
        else:
            street_address = addy[0] + ' ' + addy[1]
            city, state, zip_code = addy_ext(addy[2])

        street_address = street_address.replace('call for directions', '')
        if '(' in street_address:
            street_address = street_address.split('(')[0]

        phone_number = driver.find_element_by_css_selector('div.phone').text.replace('Phone', '').strip()

        if 'No number available' in phone_number:
            phone_number = '<MISSING>'

        if 'Unavailable' in phone_number:
            phone_number = '<MISSING>'

        hours = driver.find_element_by_css_selector('div.hours').text.replace('Hours', '').replace('\n', ' ').strip()

        map_link = driver.find_element_by_css_selector('div.map_wrap').find_element_by_css_selector('img').get_attribute('src')

        start = map_link.find('=icon:')
        end = map_link.find('|')
        coords = map_link[start + len('=icon:'): end].split(',')

        lat = coords[0]
        longit = coords[1]
        page_url = link
        country_code = 'US'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
