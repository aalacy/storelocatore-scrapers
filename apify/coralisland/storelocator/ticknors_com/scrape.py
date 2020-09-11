import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--start-maximized")
driver = webdriver.Chrome('chromedriver', options=options)

base_url = 'https://ticknors.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '')
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://ticknors.com/pages/stores"
    driver.get(url)
    source = driver.page_source
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="page-details-block block__map"]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath('.//h2[@class="title"]//text()'))) #location name
        details = eliminate_space(store.xpath('.//p/text()'))        
        address = parse_address(validate(details[:2]))
        output.append(address['street']) #address
        output.append(address['city']) #city
        if len(address['state']) > 3:
            output.append(address['state'][:2]) #state
            output.append(address['state'][2:]) #zipcode  
        else:
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//p/a/text()'))) #phone
        output.append("Ticknors Men's Clothiers") #location type
        geo_loc = validate(store.xpath('.//div[@class="featured-link--half"]//a/@href')[-1]).split('/@')[1].split(',')
        output.append(get_value(geo_loc[0])) #latitude
        output.append(get_value(geo_loc[1])) #longitude
        output.append(validate(details[2:])) #opening hours
        output_list.append(output)
    driver.close()
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
