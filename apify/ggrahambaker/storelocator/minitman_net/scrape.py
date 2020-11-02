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

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.minitman.net/'
    ext = 'minitman-store-locator/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    driver.implicitly_wait(10)
    time.sleep(10)
    locs = driver.find_elements_by_css_selector('div.results_entry')
    all_store_data = []
    for loc in locs:
        tds = loc.find_elements_by_css_selector('td')
        
        location_name = tds[0].text
        
        store_number = location_name.split('#')[-1].strip()
        
        addy = tds[1].text.split('\n')
        street_address = addy[0]
        
        city, state, zip_code = addy_ext(addy[1])
        
        links = tds[2].find_elements_by_css_selector('a')
        if len(links) == 2:
            page_url = links[-1].get_attribute('href')
        else:
            page_url = '<MISSING>'
        
        hours = '<MISSING>'
        country_code = 'US'
        longit = '<MISSING>'
        lat = '<MISSING>'
        phone_number = '<MISSING>'
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
