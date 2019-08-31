import csv
import re

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
driver = webdriver.Chrome('chromedriver', options=options)

BASE_URL = 'http://sleepexperts.com'
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

def remove_non_ascii_characters(string):
    return ''.join([i if ord(i) < 128 else '' for i in string]).strip()

def parse_google_maps_url(url):
    return re.findall(r'@(-?\d*.{1}\d*,-?\d*.{1}\d*)', url)[0].split(',')

def parse_address(address):
    return [
        remove_non_ascii_characters(item.replace('<br>', '').replace(',', ''))
        for item in address.split('\n')
        if len(item.strip())
    ]

def fetch_data():
    data = []
    driver.get('http://sleepexperts.com/stores')
    stores = driver.find_elements_by_css_selector('div.store-square')
    for store in stores:
        location_name = store.find_element_by_css_selector('div.store-name').get_attribute('innerText')
        try:
            location_type = store.find_element_by_css_selector('div.store-blurb').get_attribute('innerText').strip()
            location_type = 'Sleep Expert Super Center' if location_type == 'SUPER CENTER' else 'Sleep Expert Store'
        except NoSuchElementException:
            location_type = 'Sleep Expert Store'
        address = store.find_element_by_css_selector('div.store-address').get_attribute('innerHTML')
        street_address, city, state, zipcode = parse_address(address)
        phone = store.find_element_by_css_selector('a[href*="tel:"]').get_attribute('innerText')
        store_url = store.find_element_by_css_selector('div.store-link a').get_attribute('href')
        data.append([
            BASE_URL,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            MISSING,
            phone,
            location_type,
            store_url
        ])
    for idx, store in enumerate(data):
        store_url = store.pop()
        driver.get(store_url)
        google_maps_url = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.store-map-large-link a'))
        ).get_attribute('href')
        hours_of_operation = " | ".join([
            " ".join(item.get_attribute('innerText').split())
            for item in driver.find_elements_by_css_selector('table.store-hours tr')
        ])
        driver.get(google_maps_url)
        WebDriverWait(driver, 30).until(
            EC.url_contains('@')
        )
        lat, lon = parse_google_maps_url(driver.current_url)
        store.extend([
            lat,
            lon,
            hours_of_operation
        ])
        data[idx] = store
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
