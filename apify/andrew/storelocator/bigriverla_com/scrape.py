import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

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

def parse_geo(url):
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon

def fetch_data():
    data = []
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)
    driver = webdriver.Chrome('/bin/chromedriver', chrome_options=options)
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
        lat, lon = parse_geo(driver.find_element_by_css_selector('iframe').get_attribute('src'))
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
            lat,
            lon,
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
