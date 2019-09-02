import csv
import re
import pdb
import requests
from lxml import etree
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--start-maximized")
driver = webdriver.Chrome('chromedriver', options=options)


base_url = 'https://freebirds.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://freebirds.com/api/restaurants?includePrivate=false"
    session = requests.Session()
    request = session.get(url)
    driver.get('https://freebirds.com/locations')
    source = driver.page_source.encode('ascii', 'ignore').encode("utf8")
    time.sleep(15)
    # bt_element_present = EC.presence_of_element_located((By.CLASS, 'row golden-links'))
    # WebDriverWait(driver, 10).until(elements)
    store_hours = etree.HTML(source).xpath('.//div[@class="container m-auto location-cont"]')
    store_list = json.loads(request.text)['restaurants']
    for idx, store in enumerate(store_list):
        output = []
        output.append(base_url) # url
        output.append(store['name']) #location name
        output.append(store['streetaddress']) #address
        output.append(store['city']) #city
        output.append(store['state']) #state
        output.append(store['zip']) #zipcode
        output.append('US') #country code
        output.append(store['id']) #store_number
        output.append(store['telephone']) #phone
        output.append('<MISSING>') #location type
        output.append(store['latitude']) #latitude
        output.append(store['longitude']) #longitude
        output.append(''.join(store_hours[idx].xpath('.//strong//text()'))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
