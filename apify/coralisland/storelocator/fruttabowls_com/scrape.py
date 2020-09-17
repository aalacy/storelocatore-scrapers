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

base_url = 'https://www.fruttabowls.com'


def validate(items):
    rets = []
    for item in items:
        item = item.replace('\u202d', '').replace('\u202c', '').replace('\xa0', '').strip()
        if item == '':
            item = '<MISSING>'
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
    url = "https://www.fruttabowls.com/find-a-location/"
    driver.get(url)
    source = driver.page_source
    response = etree.HTML(source)
    temp = '[' + source.split('locations: [')[1].split('apiKey:')[0].strip()[:-1]
    store_list = json.loads(temp)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(store['name']) #location name
        output.append(store['street']) #address
        output.append(store['city']) #city
        output.append(store['state']) #state
        output.append(store['postal_code']) #zipcode
        output.append('US') #country code
        output.append(str(store['id'])) #store_number
        output.append(store['phone_number']) #phone
        output.append('FoodEstablishment') #location type
        output.append(str(store['lat'])) #latitude
        output.append(str(store['lng'])) #longitude
        output.append(' '.join(etree.HTML(store['hours']).xpath('.//text()'))) #opening hours
        output_list.append(validate(output))
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
