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



def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    locator_domain = 'https://www.minitman.net/'
    ext = 'minitman-store-locator/'

    driver = get_driver()
    driver.get(locator_domain + ext)
    time.sleep(2)


    table = driver.find_element_by_css_selector('div#map_sidebar')
    locs = table.find_elements_by_css_selector('span.location_name')
    all_store_data = []
    for loc in locs:
        driver.execute_script("arguments[0].click();", loc)

        time.sleep(2)

        cont = driver.find_element_by_css_selector('div#sl_info_bubble').text.split('\n')
        location_name = cont[0]
        store_number = cont[0].split('#')[1].strip()
        street_address = cont[1]
        city, state, zip_code = addy_ext(cont[2])
        hours = cont[-1]

        country_code = 'US'
        page_url = '<MISSING>'
        longit = '<MISSING>'
        lat = '<MISSING>'
        phone_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

        time.sleep(3)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
