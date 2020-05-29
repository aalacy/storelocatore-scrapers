import csv
import os
from sgselenium import SgSelenium
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    if len(state_zip) == 3:
        state = state_zip[0] + ' ' + state_zip[1]
        zip_code = state_zip[2]
    else:
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://5starnutritionusa.com/'
    ext = 'pages/store-locator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    lis = driver.find_elements_by_css_selector('li.stockist-list-result')

    all_store_data = []
    for li in lis:
        location_name = li.find_element_by_css_selector('div.stockist-result-name').text

        street_address = li.find_element_by_css_selector('div.stockist-result-addr-1').text
        rest = li.find_element_by_css_selector('div.stockist-result-addr-locality').text.split(',')
        city = rest[0].strip()
        state_zip = rest[1].strip().split(' ')
        if len(state_zip) == 3:
            state = state_zip[0] + ' ' + state_zip[1]
            zip_code = state_zip[2]
        else:
            if len(state_zip) == 1:
                state = state_zip[0]
                zip_code = '<MISSING>'
            else:
                state = state_zip[0]
                zip_code = state_zip[1]

        phone_number = street_address = li.find_element_by_css_selector('div.stockist-result-phone').text

        try:
            hours = li.find_element_by_css_selector('div.stockist-result-notes').text.replace('\n', ' ')
        except:
            hours = '<MISSING>'

        country_code = 'US'
        store_number = '<MISSING>'
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
