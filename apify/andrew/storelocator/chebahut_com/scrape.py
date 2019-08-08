import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver', options=options)

BASE_URL = 'https://chebahut.com'
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

def fetch_data():
    data = []
    driver.get('https://chebahut.com/locations')
    stores = driver.find_elements_by_css_selector('div[id*="location-box"]')
    for store in stores:
        is_open = 'display: none' in store.find_element_by_css_selector('p.mb-1 span:nth-child(2)').get_attribute('style')
        if not is_open:
            continue
        location_name = store.find_element_by_css_selector('p.mb-1') \
            .get_attribute('innerText') \
            .split('\n')[0] \
            .strip()
        address = store.find_element_by_css_selector('address').get_attribute('innerText')
        street_address, city, state = [
            remove_non_ascii_characters(item) for item in address.split(',')
        ]
        store_url = store.find_element_by_css_selector('p.location-links a:nth-child(1)').get_attribute('href')
        data.append([
            BASE_URL,
            location_name,
            street_address,
            city,
            state,
            store_url
        ])
    for idx, store in enumerate(data):
        store_url = store.pop()
        driver.get(store_url)
        phone = driver.find_element_by_css_selector('a[href*="tel"]') \
            .get_attribute('href') \
            .replace('tel:', '')
        google_maps_url = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='@']"))
        ).get_attribute('href')
        lat, lon = parse_google_maps_url(google_maps_url)
        driver.get(store_url + '/drop-a-dime')
        zipcode = re.findall(
            r'\d{5}',
            driver.find_element_by_css_selector('address p:nth-of-type(1)').get_attribute('innerText')
        )[0]
        hours_of_operation = driver.find_element_by_css_selector('address p:nth-of-type(2)').get_attribute('innerText')
        if not len(hours_of_operation):
            hours_of_operation = MISSING
        store.extend([
            zipcode,
            'US',
            MISSING,
            phone,
            MISSING,
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
