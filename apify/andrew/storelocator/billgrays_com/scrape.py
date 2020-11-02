import csv
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

MISSING = "<MISSING>"
INACCESSIBLE = "<INACCESSIBLE>"
BILL_GRAYS_STORE_LOCATOR_URL = "https://www.billgrays.com/index.cfm?Page=Bill%20Grays%20Locations"

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

DRIVER = get_driver()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_stores():
    DRIVER.get(BILL_GRAYS_STORE_LOCATOR_URL)
    script_el = DRIVER.find_element_by_xpath("//script[@type='application/ld+json']")
    script_dict = json.loads(script_el.get_attribute('innerHTML'))
    stores = script_dict['@graph']
    stores = stores[1:]
    names = [store['name'] for store in stores]
    return stores

def fetch_data():
    data = []
    data.extend(fetch_stores())
    return data

def scrape():
    global DRIVER
    data = fetch_data()
    DRIVER.quit()
    write_output(data)

scrape()
