import csv
import re
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/bin/chromedriver', options=options)

BASE_URL = 'https://www.steinmart.com'
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

def fetch_street_address(address):
    return " ".join([
        address[key]
        for key in ['street1', 'street2', 'street3']
        if address[key]
    ])


def fetch_data():
    data = []
    store_urls = []
    driver.get('https://www.steinmart.com/store-locator/all-stores.do')
    store_urls = [
        a_tag.get_attribute('href')
        for a_tag in driver.find_elements_by_css_selector('div.ml-storelocator-item-wrapper a')
    ]
    for idx, store_url in enumerate(store_urls):
        print(f'{idx} of {len(store_urls)}')
        driver.get(store_url)
        script = [
            script.get_attribute('innerText')
            for script in driver.find_elements_by_css_selector('script[type="text/javascript"]')
            if 'latitude' in script.get_attribute('innerText')
        ][0]
        script = json.loads(re.findall(r'{.*}', script)[0])
        store_data = script['results'][0]
        address = store_data['address']
        street_address = fetch_street_address(address)
        hours_of_operation = " | ".join([
            tr.text.strip()
            for tr in driver.find_elements_by_css_selector('div.ml-storelocator-hours tr')
        ])
        data.append([
            BASE_URL,
            store_data.get('name'),
            street_address,
            address.get('city'),
            address.get('stateCode'),
            address.get('postalCode'),
            address.get('countryName'),
            store_data.get('id'),
            address.get('phone'),
            MISSING,
            store_data.get('location', {}).get('latitude'),
            store_data.get('location', {}).get('longitude'),
            hours_of_operation
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
