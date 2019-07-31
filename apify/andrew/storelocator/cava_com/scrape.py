import csv
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/bin/chromedriver', options=options)

BASE_URL = 'https://cava.com/locations'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    driver.get(BASE_URL)
    stores = driver.find_elements_by_css_selector('div.vcard')
    for store in stores:
        location_name = store.find_element_by_css_selector('h3').text
        street_address = store.find_element_by_css_selector('div.street-address').text
        city = store.find_element_by_css_selector('span.locality').text.replace(',', '')
        state = store.find_element_by_css_selector('span.region').text
        zipcode = store.find_element_by_css_selector('span.postal-code').text
        try:
            hours_of_operation = store.find_element_by_css_selector('p.copy').text
        except NoSuchElementException:
            hours_of_operation = '<MISSING>'
            continue
        phone = store.find_element_by_css_selector('div.vcard > div.adr > div > a').text
        try:
            store_number = store.find_element_by_css_selector("div.adr ~ p > a[href*='order.cava.com']").get_attribute('href')
            store_number = re.findall(r'stores\/{1}(\d*)', store_number)[0]
        except NoSuchElementException:
            store_number = '<MISSING>'
        data.append([
            'https://cava.com',
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
            hours_of_operation
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
