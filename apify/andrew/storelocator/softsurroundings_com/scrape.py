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

BASE_URL = 'https://www.softsurroundings.com'
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

def parse_address(address):
    zipcode = re.findall(r' \d{5}', address)[0]
    address = address.replace(zipcode, '')
    city, state = address.split(',')
    return [
        remove_non_ascii_characters(item)
        for item in [city, state, zipcode]
    ]

def parse_google_maps_url(url):
    return re.findall(r'@(-?\d*.{1}\d*,-?\d*.{1}\d*)', url)[0].split(',')

def fetch_data():
    data = []
    driver.get('https://www.softsurroundings.com/stores/all/')
    store_urls = [
        a_tag.get_attribute('href')
        for a_tag in driver.find_elements_by_css_selector('ul.storeBlock li a')
    ]
    for store_url in store_urls:
        driver.get(store_url)
        location_name = " ".join([
            item.capitalize()
            for item in driver.find_element_by_css_selector('h2.storeName').text.split()
        ])
        street_address, address, phone = [
            li.text.strip()
            for li in driver.find_elements_by_css_selector('ul.storeList li')[:3]
        ]
        city, state, zipcode = parse_address(address)
        state = re.findall(r'[A-Z]{2}', state)[0]
        store_number = driver.find_element_by_css_selector("input[id='storeId']") \
            .get_attribute('value')
        hours_of_operation = driver.find_element_by_css_selector("h4 ~ p") \
            .text \
            .replace("Now Open", '').replace("Now open", '') \
            .replace("!", '') \
            .strip()
        if 'Opening' in hours_of_operation: continue
        google_maps_url = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='@']"))
        ).get_attribute('href')
        lat, lon = parse_google_maps_url(google_maps_url)
        data.append([
            BASE_URL,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            store_number,
            phone,
            MISSING,
            lat,
            lon,
            hours_of_operation
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
