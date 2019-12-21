import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code



def fetch_data():
    locator_domain = 'http://www.urbancookhouse.com/'
    ext = 'location/'

    driver = get_driver()
    driver.get(locator_domain + ext)
    time.sleep(3)
    driver.implicitly_wait(30)
    
    locs = driver.find_elements_by_css_selector('div.location-info')

    all_store_data = []
    for loc in locs:
        location_name = loc.find_element_by_css_selector('span.location-title').text
        
        if 'MONTGOMERY' in location_name:
             address = loc.find_elements_by_css_selector('a')[1]
        else:
            address = loc.find_element_by_css_selector('span.address').find_element_by_css_selector('a')
        street_address = address.text.split('\n')[0]
        city, state, zip_code = addy_ext(address.text.split('\n')[1])


        href = address.get_attribute('href')
        start_idx = href.find('/@')
        end_idx = href.find('z/data')
        coords = href[start_idx + 2:end_idx].split(',')

        lat = coords[0]
        longit = coords[1]

        phone_number = loc.find_element_by_css_selector('span.location-phone').find_element_by_css_selector('a').text
        if 'TUSCALOOSA' in location_name:
            hours = '<MISSING>'
        else:
            hours = loc.find_element_by_css_selector('span.hours').text.replace('\n', ' ')


        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)



    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
