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
    locator_domain = 'https://www.mhs.net/'
    ext = 'locations/search-results'

    driver = SgSelenium().chrome()

    driver.get(locator_domain + ext)
    no_link = 0
    link_list = []
    while no_link < 4:
        
        locs = driver.find_elements_by_css_selector('div.listing-item')
        
        for loc in locs:
            link = loc.find_element_by_css_selector('a.button').get_attribute('href')
            link_list.append(link)
            
        no_link += len(driver.find_elements_by_css_selector('li.arrow.no-link'))
        
        url = driver.find_elements_by_css_selector('li.arrow')[1].find_element_by_css_selector('a').get_attribute('href')
        if url == None:
            break
        driver.get(url)
        driver.implicitly_wait(5)
        
        time.sleep(4)

    all_store_data = []
    for link in link_list:
        
        driver.get(link)
        driver.implicitly_wait(5)
        
        location_name = driver.find_element_by_css_selector('h1').text
        info_raw = driver.find_element_by_css_selector('div.module-lc-address').text.split('\n')
        info = []
        for i in info_raw:
            if 'Suite' in i and ',' not in i:
                continue
            if 'Outpatient' in i:
                continue
            if 'Lobby' in i:
                continue
            if 'Community Center' in i:
                continue
            info.append(i)
                
        street_address = info[0]
        street_address = street_address.split('Suite')[0].strip().split('Unit')[0].strip().replace(',', '').strip()

        city, state, zip_code = addy_ext(info[1])

        phone_number = info[2].replace('Phone:', '').strip()
        if 'Maps' in phone_number:
            phone_number = '<MISSING>'
            
        hours =  driver.find_element_by_css_selector('div.module-lc-hours').text.replace('\n', ' ').replace('Hours', '').strip()
        hours = hours.split('Email')[0]
        
        country_code = 'US'
        store_number = '<MISSING>'
        
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
