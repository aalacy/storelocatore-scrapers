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

base_url = 'https://www.newyorkpilates.com/'

missing = '<MISSING>'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
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
    url = "https://www.newyorkpilates.com/"
    driver.get(url)
    source = driver.page_source
    response = etree.HTML(source)
    store_list = response.xpath('.//div[@class="footer-wrapper fullwidth-footer"]//div[@class="mk-padding-wrapper"]//div[@class="mk-col-1-5"]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath('.//div[@class="widgettitle"]//text()'))) #location nam
        address = eliminate_space(store.xpath('.//div[@class="textwidget"]//text()'))
        output.append(' '.join(address[:-1])) #address
        output.append(validate(address[-1].split(',')[0])) #city
        output.append(validate(address[-1].split(',')[1]).split(' ')[0]) #state
        output.append(validate(address[-1].split(',')[1]).split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append(missing) #store_number
        output.append(missing) #phone
        output.append('NEW YORK PILATES') #location type
        output.append(missing) #latitude
        output.append(missing) #longitude
        link = base_url + validate(store.xpath('.//div[@class="widgettitle"]//a/@href'))
        driver.get(link)
        data = etree.HTML(driver.page_source)
        store_hours = data.xpath('.//div[contains(@class, "mk-text-block")]')
        if len(store_hours) > 0:
            store_hours = ', '.join(eliminate_space(store_hours[0].xpath('.//p//text()')))
            if 'hurs' not in store_hours.lower():
                store_hours = missing
        else :
            store_hours = missing
        output.append(store_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
