import csv
import re
import json
import usaddress

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from constants import US_STATE_ABBREV

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver', options=options)

BASE_URL = 'https://www.snappytomato.com/'
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

def parse_address(address, state):
    _address = address.replace('<br />', '')
    address = address.replace('{} '.format(state), '') \
        .replace('{} '.format(US_STATE_ABBREV[state]), '')
    address = address.split('<br />')
    city_zipcode = address.pop()
    zipcode = re.findall(r'\d{5}', city_zipcode)[0]
    city = city_zipcode.replace(zipcode, '')
    city = city.replace(',', '').replace('\n', '')
    if len(address) == 1:
        street_address  = address[0]
    else:
        street_address = " ".join([
            item.strip()
            for item in address
        ])
    if city == '':
        city = usaddress.tag(_address)[0]['PlaceName']
    return [
        remove_non_ascii_characters(item)
        for item in [street_address, city, zipcode]
    ]

def fetch_data():
    data = []
    driver.get('https://www.snappytomato.com/locations/')
    store_urls_by_state = [
        (
            " ".join([
                item.strip().capitalize()
                for item in state_container.find_element_by_css_selector('h3').text.split()
            ]),
            [
                a_tag.get_attribute('href') 
                for a_tag in state_container.find_elements_by_css_selector('li a')
            ]
        )
        for state_container in driver.find_elements_by_css_selector('div.single-state')
    ]
    for state, store_urls in store_urls_by_state:
        for store_url in store_urls:
            driver.get(store_url)
            try:
                script = [
                script.get_attribute('innerText')
                for script in driver.find_elements_by_css_selector("script:not([src])[type='text/javascript']")
                if 'singleLocation' in script.get_attribute('innerText')
            ][0]
            except:
                continue #new location
            store_data = json.loads(
                re.findall(r'Snappy = ({.*})', script)[0]
            )['singleLocation']
            street_address, city, zipcode = parse_address(store_data['address'], state)
            hours_of_operation = " | ".join([
                item.strip()
                for item in store_data['hours'].split('<br />')
            ])
            phone = store_data['phone'] if len(store_data['phone']) else MISSING
            data.append([
                BASE_URL,
                store_data['storeName'],
                street_address,
                city,
                state,
                zipcode,
                'US',
                store_data['ID'],
                phone,
                MISSING,
                store_data['lat'],
                store_data['lng'],
                hours_of_operation
            ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
