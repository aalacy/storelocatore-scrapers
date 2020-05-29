import csv
import os
from sgselenium import SgSelenium
import time

def addy_extractor(state_city):
    city = state_city.split(',')[0]
    state_zip = state_city.split(',')[1].strip().split(' ')
    if len(state_zip) == 2:
        state = state_zip[0]
        zip_code = state_zip[1][0:3] + ' ' + state_zip[1][3:]
    else:
        state = state_zip[0]
        zip_code = state_zip[1] + ' ' + state_zip[2]
    
    return city.strip(), state.strip(), zip_code.strip()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.firehousesubs.ca/'
    ext = 'all-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('section.locations_wrap')
    locs = main.find_elements_by_css_selector('article')
    link_list = []
    for loc in locs:
        cont = loc.text.split('\n')
        phone_number = cont[-1]
        
        link = loc.find_element_by_css_selector('a').get_attribute('href')
        if 'Coming Soon' in cont[0]:
            continue
        
        link_list.append([link, phone_number, cont[0]])

    all_store_data = []
    for cont in link_list:
        driver.get(cont[0])
        
        time.sleep(2)
        driver.implicitly_wait(10)

        phone_number = cont[1]
        div_info = driver.find_element_by_css_selector('div#SiteInfoDiv').text.split('\n')
        
        name_and_number = cont[2].split('#')
        
        store_number = name_and_number[1].strip()
        location_name = name_and_number[0].strip()
        
        street_address = div_info[1]
        city, state, zip_code = addy_extractor(div_info[2])
        
        country_code = 'CA'

        location_type = '<MISSING>'
        page_url = cont[0]
        hours = '<MISSING>'
        longit = '<MISSING>'
        lat = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
