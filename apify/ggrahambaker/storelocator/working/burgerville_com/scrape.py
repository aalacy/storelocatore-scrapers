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



def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code



def fetch_data():
    locator_domain = 'https://www.burgerville.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    loc_list = driver.find_element_by_id('map_sidebar_toggle')
    driver.execute_script("arguments[0].click();", loc_list)

    main = driver.find_element_by_id('map_sidebar')
    locs = main.find_elements_by_css_selector('div.results_wrapper')
    all_store_data = []
    for l in locs:
        cont = l.text.split('\n')
        cut = cont[0].find('(')
        location_name = cont[0][:cut].strip()

        store_number = cont[0][cut + 1:-1].replace('#', '')
        if 'Signature' in store_number:
            store_number = '<MISSING>'

        street_address = cont[2]
        city, state, zip_code = addy_ext(cont[3])
        if len(cont) == 7:
            phone_number = cont[4]
        else:
            phone_number = cont[5]

        country_code = 'US'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
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
