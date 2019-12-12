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
    locator_domain = 'https://www.krispykreme.ca/'
    ext = 'find-a-store/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('div.store-section')
    all_store_data = []
    for loc in locs:
        
        cont = loc.text.split('\n')
        
        if len(cont) == 9:
            off = 1
        else:
            off = 0
            
        location_name = cont[0]
        street_address = cont[1].split('(')[0].strip()
        city_state = cont[off + 2].split(' ')
        if len(city_state) == 3:
            city = city_state[0] + ' ' + city_state[1]
            state = city_state[2]
        else:
            city = city_state[0]
            state = city_state[1]
        
        zip_code = cont[off + 3]
        
        phone_number = cont[off + 4]
        
        if len(cont) == 7:
            hours = cont[off + 6]
        else:
            hours = cont[off + 6] + ' ' + cont[off + 7]
        
        
        
        gmap_script = loc.find_element_by_css_selector('div.store-section-map').find_element_by_css_selector('script').get_attribute('innerHTML')
        
        start = gmap_script.find('.LatLng(')
        temp = gmap_script[start + len('.LatLng('):]
        end = temp.find(')')
        coords = temp[:end].split(',')

        lat = coords[0]
        longit = coords[1]

        
        country_code = 'CA'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
        store_number = '<MISSING>'
        
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
