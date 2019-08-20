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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://coqobec.net/'

    driver = get_driver()
    driver.get(locator_domain)
    cell = \
    driver.find_element_by_css_selector('table').find_element_by_css_selector('tr').find_elements_by_css_selector('th')[
        5]

    table = cell.find_element_by_css_selector('tbody')
    trs = table.find_elements_by_css_selector('tr')

    all_store_data = []
    for tr in trs:
        ths = tr.find_elements_by_css_selector('th')
        for th in ths:
            cont = th.text.split('\n')
            if len(cont) == 1:
                continue

            location_name = cont[0]
            street_address = cont[1].replace(',', '')
            addy = cont[2].split(',')
            city = addy[0]
            state = addy[1].strip()
            zip_code = '<MISSING>'

            phone_number = cont[3]

            lat = '<MISSING>'
            longit = '<MISSING>'

            country_code = 'US'
            location_type = '<MISSING>'
            store_number = '<MISSING>'
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
