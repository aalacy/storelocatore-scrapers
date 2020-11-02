import csv
import re
import pdb
import requests
from lxml import etree
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--start-maximized")
driver = webdriver.Chrome('chromedriver', options=options)

base_url = 'https://www.britishbeer.com'

def validate(items):
    rets = []
    for item in items:
        item = item.replace('\u202d', '').replace('\u202c', '').replace('\xa0', '').strip()
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.britishbeer.com/pages/find-your-local"
    driver.get(url)
    source = driver.page_source
    response = etree.HTML(source)
    store_list = response.xpath('//script[@type="application/ld+json"]')
    store_hours = response.xpath('//div[@class="pm-location-search-list"]//div[@class="hours"]')
    for idx, store in enumerate(store_list):
        output = []
        store = json.loads(store.xpath('.//text()')[0])
        output.append(base_url) # url
        output.append(store['name']) #location name
        output.append(store['address']['streetAddress']) #address
        output.append(store['address']['addressLocality']) #city
        output.append(store['address']['addressRegion']) #state
        output.append(store['address']['postalCode']) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(store['telephone']) #phone
        output.append(store['@type']) #location type
        output.append('<MISSING>') #latitude
        output.append('<MISSING>') #longitude
        output.append(' '.join(validate(store_hours[idx].xpath('.//text()')))) #opening hours
        output_list.append(validate(output))
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
