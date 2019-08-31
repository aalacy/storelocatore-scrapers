import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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



def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    locator_domain = 'https://www.myapplemarket.com/'

    driver = get_driver()
    driver.get(locator_domain)

    stores = driver.find_elements_by_css_selector('div.LocalBusiness')

    all_store_data = []
    for i, store in enumerate(stores):
        content = store.text.split('\n')
        street_address = content[0]
        city, state, zip_code = addy_ext(content[1])
        phone_number = content[2].replace('Phone:', '').strip()

        if i < 3:
            location_type = 'Country Harvest Apple Markets'
        elif i < 4:
            location_type = "Jim's Foodliner Apple Market"
        elif i < 5:
            location_type = 'Seabrook Apple Market'
        elif i < 6:
            location_type = "Ray's Apple Markets"

        location_name = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
