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

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code




def fetch_data():
    locator_domain = 'https://www.cafebizou.com/'
    ext = 'location/agoura-hills/'

    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.execute_script("window.scrollTo(0, 1000)")
    time.sleep(10)


    main = driver.find_element_by_css_selector('section#intro').text.split('\n')
    all_store_data = []

    street_address = main[1]
    city, state, zip_code = addy_ext(main[2])
    phone_number = main[3]
    hours = ''
    for h in main[5:]:
        hours += ' '.join(h.split()) + ' '

    hours = hours.strip()

    location_name = '<MISSING>'
    lat = '<MISSING>'
    longit = '<MISSING>'

    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]
    all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
