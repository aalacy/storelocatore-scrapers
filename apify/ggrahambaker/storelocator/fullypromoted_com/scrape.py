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

def addy_ext_can(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1] + ' ' + state_zip[2]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://fullypromoted.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    driver.get(locator_domain + ext)
    locs = driver.find_elements_by_css_selector('li.py-4.brdr-b1.brdr-c-grey')

    link_list = []
    for loc in locs:
        link_list.append(loc.find_element_by_css_selector('a').get_attribute('href'))

    ## canada locs
    ## they dont have individual pages for canada locs
    driver.get('https://fullypromoted.com/locations/country/can/')
    driver.implicitly_wait(10)
    locs = driver.find_elements_by_css_selector('li.py-4.brdr-b1.brdr-c-grey')
    all_store_data = []
    for loc in locs:
        content = loc.text.split('\n')
        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext_can(content[3])
        phone_number = content[4]

        country_code = 'CA'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(30)

        loc_j = driver.find_elements_by_xpath('//script[@type="application/ld+json"]')

        loc_json = json.loads(loc_j[1].get_attribute('innerHTML'))

        lat = loc_json['geo']['latitude']
        longit = loc_json['geo']['longitude']

        loc = driver.find_element_by_css_selector('div.pt-2.pb-4.px-4')

        content = loc.text.split('\n')
        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[3].replace('Call us:', '').strip()
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        hours = driver.find_element_by_css_selector('tbody').text.replace('\n', ' ')

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
