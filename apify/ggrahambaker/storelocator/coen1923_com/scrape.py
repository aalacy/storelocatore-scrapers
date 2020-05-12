import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import time

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
    locator_domain = 'https://coen1923.com/'
    ext = 'locations'

    driver = get_driver()
    driver.get(locator_domain + ext)

    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    url = 'https://coen1923.com/locations/search' 
    r = session.get(url, headers = HEADERS)

    locs = json.loads(r.content)['locations']

    all_store_data = []
    for loc in locs:
        try:
            location_name = loc['title']
        except:
            continue
        to_click = "showstore('" + loc['url_title'] + "');"
        
        street_address = loc['address'].replace('<p>', '').replace('</p>', '')
        city = loc['city']
        state = loc['state']
        zip_code = loc['zip']
        phone_number = loc['phone_number']
        
        coords = loc['coordinates']
        lat = coords[0]
        longit = coords[1]
        driver.execute_script('return ' + to_click)
        driver.implicitly_wait(5)
        time.sleep(1)
        
        hours = driver.find_element_by_css_selector('div.loc-head').text.replace('\n', ' ').replace('Business Hours', '').strip()        
        
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        print(store_data)
        all_store_data.append(store_data)
        
        print()
        print()
        print()


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
