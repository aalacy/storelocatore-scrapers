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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.newyorkfries.com/'
    ext = 'locations/all'

    driver = get_driver()
    driver.get(locator_domain + ext)
    main = driver.find_element_by_css_selector('div.canada')
    locs = main.find_elements_by_xpath('//span[@role="row"]')

    all_store_data = []
    for loc in locs:
        driver.execute_script("arguments[0].classList.add('open');", loc)
        cont = loc.find_element_by_css_selector('div.location-title').text.split('\n')
        if 'Bahrain City Centre Mall' in cont[0]:
            break
        time.sleep(.1)
        location_name = cont[0]
        city = cont[-2]
        state = cont[-1]

        street_address = loc.find_element_by_css_selector('div.location-info').text

        hours = '<MISSING>'
        zip_code = '<MISSING>'

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        phone_number = '<MISSING>'
        country_code = 'CA'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
