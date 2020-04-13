import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.abingtonhealth.org/'
    ext = 'our-locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    locs = driver.execute_script('return markers')

    all_store_data = []
    for loc in locs:
        street_address = loc['address'] + ' ' + loc['address2']
        street_address = street_address.strip()
        
        city = loc['city']
        state = loc['state']
        zip_code = loc['zip']
        
        lat = loc['lat']
        longit = loc['lng']
        
        location_name = loc['name']
        location_type = loc['legend']
        phone_number = loc['phone'].strip()
        if phone_number == '':
            phone_number = '<MISSING>'
        
        if loc['url'] == '':
            page_url = '<MISSING>'
        else:
            page_url = locator_domain[:-1] + loc['url']
            
            
        country_code = 'US'
        store_number = '<MISSING>'
        hours = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
