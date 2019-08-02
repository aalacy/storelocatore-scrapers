import csv
import re

from constants import US_STATE_ABBREV

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/bin/chromedriver', options=options)

BASE_URL = 'https://skippers.com'
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

def extract_inner_text(container, selector):
    return remove_non_ascii_characters(
        container.find_element_by_css_selector(selector).get_attribute('innerText')
    )

def parse_google_maps_url(url):
    return re.findall(r'@(-?\d*.{1}\d*,-?\d*.{1}\d*)', url)[0].split(',')

def parse_address(address, state):
    state_abbrev = US_STATE_ABBREV[state]
    address = address.replace(state_abbrev, '').replace(state, '')
    try:
        zipcode = re.findall(r' \d{5,}', address)[0]
    except:
        zipcode = INACCESSIBLE
    address = address.replace(zipcode, '').strip()
    if address.count(',') >= 2:
        street_address, city = address.split(',')[:2]
    else:
        street_address, city = [INACCESSIBLE]*2
    return [
        remove_non_ascii_characters(item)
        for item in [street_address, city, zipcode]
    ]


def fetch_data():
    data = []
    driver.get('https://skippers.com/skippers-locations/')
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="location-box"]'))
    )
    states_by_location_type = [
        (
            remove_non_ascii_characters(location_type.find_element_by_css_selector('h3.location-title').text),
            location_type.find_element_by_css_selector('div.state-box')
        )
        for location_type in driver.find_elements_by_css_selector('article')
    ]
    for location_type, state_container in states_by_location_type:
        state = state_container.find_element_by_css_selector('h3').text
        stores = state_container.find_elements_by_css_selector('div[class*="location-box"]')
        for store in stores:
            location_name = extract_inner_text(store, 'h3')
            address = extract_inner_text(store, 'div.location-addy')
            street_address, city, zipcode = parse_address(address, state)
            google_map_url = store.find_element_by_css_selector('div.location-map-link a').get_attribute('href')
            try:
                lat, lon = parse_google_maps_url(google_map_url)
            except:
                lat, lon = [MISSING]*2
            phone = extract_inner_text(store, 'div.location-phone')
            if not sum(char.isdigit() for char in phone) == 10:
                if phone == 'NA':
                    phone = MISSING
                else:
                    phone = INACCESSIBLE
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
                lat,
                lon,
                MISSING
            ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
