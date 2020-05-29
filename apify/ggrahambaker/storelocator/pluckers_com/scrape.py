import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

#helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    return city, state, zip_code

def fetch_data():
    data = []
    driver = SgSelenium().chrome()

    locator_domain = 'https://www.pluckers.com/'
    ext = 'locations'
    driver.get(locator_domain + ext)
    store_name = driver.find_elements_by_css_selector('div.storepoint-location')

    all_store_data = []
    for store in store_name:
        # location name
        # print(store.find_element_by_css_selector('div.storepoint-name').text)
        location_name = store.find_element_by_css_selector('div.storepoint-name').text

        # address 
        #print(store.find_element_by_css_selector('div.storepoint-address').text)  
        loc = store.find_element_by_css_selector('div.storepoint-address').text      
        if '\n' in loc:
            loc_split = loc.split('\n')
            # street_address 
            street_address = loc_split[0]
            if len(loc_split[1].split(',')) > 2:
                street_address += loc_split[1].split(',')[0]
                city, state, zip_code = addy_extractor((loc_split[1].split(',')[1] + ',' + loc_split[1].split(',')[2]).strip())
            else:
                city, state, zip_code = addy_extractor(loc_split[1])
        else:
            space_split = loc.split(' ')
            street_address = space_split[0] + ' ' + space_split[1] + ' ' + space_split[2] 
            if len(space_split) > 6:
                # 2 word city
                city = space_split[3] + ' ' + space_split[4] 
            else:
                city = space_split[3]

            state = space_split[-2]
            zip_code = space_split[-1]

        phone_number = store.find_elements_by_css_selector('a')[1].text

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        hours = '<INACCESSIBLE>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, lat, longit, hours ]
        all_store_data.append(store_data)
        
    # End scraper

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
