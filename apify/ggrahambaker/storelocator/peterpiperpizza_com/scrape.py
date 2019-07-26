import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', options=options)

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
    if len(arr) > 4:
        street_address = arr[0] + ' ' + arr[1]
        city = arr[2]
        state = arr[3]
        zip_code = arr[4]
    else:
        street_address = arr[0]
        city = arr[1]
        state = arr[2]
        zip_code = arr[3]
    
    return street_address, city, state, zip_code

def fetch_data():
    data = []
    driver = get_driver()

    locator_domain = 'https://www.peterpiperpizza.com/'
    ext = 'locations/all'

    driver.get(locator_domain + ext)
    all_store_data = []
    done = False
    table_wrapper = driver.find_elements_by_css_selector('div.table_wrapper')
    for wrap in table_wrapper:
        if done:
            break
        rows = wrap.find_elements_by_css_selector('div.row')
        for row in rows:
            #print(row.find_element_by_css_selector('div.store_name').text)
            location_name = row.find_element_by_css_selector('div.store_name').text
            if location_name == 'Plaza Coronado':
                done = True
                break
            else:
                #print(row.find_elements_by_css_selector('div.address-desktop')[0].text)
                street_address, city, state, zip_code = addy_extractor(row.find_element_by_css_selector('div.address-desktop').text)
                #print(street_address, city, state, zip_code)
                phone_number = row.find_elements_by_css_selector('div.address-desktop')[1].text

                country_code = 'US'
                location_type = '<MISSING>'
                store_number = '<MISSING>'
                hours = '<MISSING>'
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
