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

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.wingsetc.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    element = driver.find_element_by_css_selector('a.view-all')
    driver.execute_script("arguments[0].click();", element)

    container = driver.find_element_by_css_selector('ul.by-state-list')
    stores = container.find_elements_by_css_selector('li.item')

    link_list = []
    for store in stores:
        a_tag = store.find_element_by_css_selector('div.site-link-wrap').find_element_by_css_selector('a')
        link_list.append(a_tag.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        if 'springfield-mo/' in link:
            continue
        driver.implicitly_wait(10)
        driver.get(link)
        start_idx = link.find('.com/')
        location_name = link[start_idx + 5: -1].replace('-', ' ')

        address = driver.find_element_by_css_selector('div.local-address')

        addr = address.text.split('\n')
        street_address = addr[1]
        city, state, zip_code = addy_ext(addr[2])
        phone_number = addr[3]

        hours_li = driver.find_element_by_css_selector('div.local-hours').find_elements_by_css_selector('li')

        hours = ''
        for li in hours_li:
            hours += li.text + ' '
        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
