import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
import json
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
    locator_domain = 'https://www.francescas.com/'
    ext = 'store-locator/all-stores.do'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    link_list = []
    locs = driver.find_elements_by_css_selector('div.eslStore.ml-storelocator-headertext')
    for loc in locs:
        link = loc.find_element_by_css_selector('a').get_attribute('href')
        
        if link == '':
            continue
        
        if link in link_list:
            continue
            
        link_list.append(link)
        
    all_store_data = []
    dup_tracker = set()
    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(10)
        time.sleep(3)

        try:
            location_name = driver.find_element_by_xpath('//span[@itemprop="name"]').text
        
        except NoSuchElementException:
            continue

        if len(location_name.split('#')) == 2:
            store_number = location_name.split('#')[1].split('-')[0].strip()
        else:
            store_number = '<MISSING>'

        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text.replace('\n', ' ')
        if street_address not in dup_tracker:
            dup_tracker.add(street_address)
        else:
            continue
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text
        state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text
        if len(zip_code) == 4:
            zip_code = '0' + zip_code
        hours = driver.find_element_by_css_selector('span.ml-storelocator-hours-details').text.replace('\n', ' ')

        try:
            phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text
        except NoSuchElementException:
            phone_number = '<MISSING>'

        loc_j = driver.find_elements_by_xpath('//script[@type="text/javascript"]')
        for i, loc in enumerate(loc_j):
            if 'MarketLive.StoreLocator.storeLocatorDetailPageReady' in loc.get_attribute('innerHTML'):
                text = loc.get_attribute('innerHTML')
                start = text.find('location')
                text_2 = text[start-1:]
                
                end = text_2.find('}')
                
                coords = json.loads(text_2[text_2.find(':') + 1:end + 1])
                
                lat = coords['latitude']
                longit = coords['longitude']
        
        country_code = 'US'
        location_type = '<MISSING>'
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
