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

BASE_URL = 'https://starcycleride.com'
MISSING = '<MISSING>'
INACCESSIBLE = '<INACCESSIBLE>'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_google_maps_url(url):
    return re.findall(r'@(-?\d*.{1}\d*,-?\d*.{1}\d*)', url)[0].split(',')

def fetch_data():
    data = []
    store_urls = []
    driver.get('https://starcycleride.com/studios/all')
    stores = driver.find_elements_by_css_selector('div.location')
    for store in stores:
        try:
            # Test to see if closed
            store.find_element_by_css_selector('span')
            continue
        except NoSuchElementException:
            pass
        store_urls.append(
            store.find_element_by_css_selector('div.location p a').get_attribute('href')
        )
    for store_url in store_urls:
        print(store_url)
        driver.get(store_url)
        store = driver.find_element_by_css_selector('div.text-center div.text-center')
        location_name = " ".join([
            item.capitalize()
            for item in store.find_element_by_css_selector("h1").text.split()
        ])
        address = store.find_element_by_css_selector('p:nth-of-type(2)').text
        zipcode = re.findall(r' \d{5}', address)[0].strip()
        address = address.replace(zipcode, '')
        _address = [
            item.strip() for item in address.split(',')
        ]
        if len(_address) == 3:
            street_address, city, state = _address
        if len(_address) == 4:
            street_address = " ".join(_address[:2])
            city = _address[2]
            state = _address[3]
        try:
            phone = store.find_element_by_css_selector("a[href*='tel:']").text
            location_type = "Current Location"
        except:
            phone = MISSING
            location_type = "Coming Soon"

        google_maps_url = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/@']"))
        ).get_attribute('href')
        lat, lon = parse_google_maps_url(google_maps_url)
        data.append([
            BASE_URL,
            store_url,
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
