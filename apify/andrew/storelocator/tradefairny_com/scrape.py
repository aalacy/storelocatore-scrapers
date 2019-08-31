import csv
import re
import usaddress

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

BASE_URL = 'https://www.tradefairny.com'
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
    zipcode = re.findall(r' \d{5}', address)[0]
    address = address.replace(zipcode, '')
    try:
        street_address, city, state = [
            item.strip() for item in address.split(',')
        ]
    except:
        city = []
        state = re.findall(r'[A-Z]{2}', address)[0]
        for value, label in usaddress.parse(address):
            if label == 'PlaceName':
                city.append(value)
        city = " ".join(city)
        street_address = address.replace(state, '').replace(city, '')
    return [
        item.rstrip(',')
        for item in [street_address, city, state, zipcode]
    ]

def fetch_data():
    data = []
    store_urls = []
    driver.get('https://www.tradefairny.com/store-locations.html')
    store_urls = [
        a_tag.get_attribute('href')
        for a_tag in driver.find_elements_by_css_selector("li > a[href*='trade-fair']")
        if not 'catering' in a_tag.get_attribute('href')
    ]
    for store_url in store_urls:
        driver.get(store_url)
        location_name, address, hours_of_operation, phone = [
            el.text.strip()
            for el in driver.find_elements_by_css_selector('div > pre > *')
            if len(el.text.strip())
        ]
        store_number = location_name.split('#')[-1]
        street_address, city, state, zipcode = parse_address(address)
        phone = re.findall(r'Store Phone: (.*) /', phone)[0]
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
            MISSING,
            MISSING,
            hours_of_operation
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
