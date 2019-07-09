import csv
import os
from selenium import webdriver
import re

MISSING = '<MISSING>'
INACCESSIBLE = '<INACCESSIBLE>'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_address(address):
    _address = address.split('\n')[1:]
    street_address = _address[0].replace(',', '')
    city, _address = _address[1].split(',')
    state, zip_code = _address.split()
    return street_address, city, state, zip_code

def parse_phone(phone):
    return phone.split('\n')[-1]

def fetch_data():
    data = []
    driver = webdriver.Chrome(f'{os.path.dirname(os.path.abspath(__file__))}/chromedriver')
    driver.get('https://www.bigriverla.com/')
    # Fetch store urls from location menu
    store_els = driver.find_elements_by_css_selector('ul#menu-big-river-main-menu > li:nth-child(3) > ul > li > a')
    store_urls = [store_el.get_attribute('href') for store_el in store_els]
    # Fetch data for each store url
    for store_url in store_urls:
        driver.get(store_url)
        # Fetch address/phone elements
        location_name = driver.find_element_by_css_selector('h1.entry-title').text
        address_el, phone_el = driver.find_elements_by_css_selector('div.wpb_column:nth-of-type(1) div.wpb_column:nth-of-type(1) p')
        # Parse address/phone elements
        street_address, city, state, zipcode = parse_address(address_el.text)
        phone = parse_phone(phone_el.text)
        # Regex match for store number in store name
        store_number = re.findall(r'#(\d+)', location_name)[0]
        data.append([
            'https://www.bigriverla.com/',
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            store_number,
            phone,
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()