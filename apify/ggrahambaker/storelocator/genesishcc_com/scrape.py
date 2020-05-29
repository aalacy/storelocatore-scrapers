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
    locator_domain = 'https://genesishcc.com/'
    ext = 'findlocations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    time.sleep(2)
    driver.implicitly_wait(5)
    locs = driver.find_elements_by_css_selector('div.p-1.nano')
    all_store_data = []
    for loc in locs:
        location_name = loc.find_element_by_css_selector('div.cI-title').text

        page_url = loc.find_element_by_css_selector('a').get_attribute('href')
        
        addy = loc.find_element_by_css_selector('div.cI-address').text.split('\n')
        if len(addy) > 3:
            addy = addy[1:]

        street_address = addy[0]
        
        city, state, zip_code = addy_ext(addy[1])
        
        country_code = 'US'
        store_number = '<MISSING>'
        
        location_type = '<MISSING>'
        
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        hours = '<MISSING>'
        
        phone_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    for data in all_store_data:
        url = data[-1].replace('https', 'http')

        while data[-6] == '<MISSING>':

            driver.get(url)

            driver.implicitly_wait(10)
            time.sleep(2)
            try:
                phone_number = driver.find_element_by_xpath('//a[contains(@href,"tel:")]').text.replace('Phone:', '').strip()
            except:
                try:
                    phone_number = driver.find_element_by_css_selector('i.fa-phone').find_element_by_xpath('..').text.replace('tel', '').strip()
                except:
       
                    continue
            data[-6] = phone_number

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
