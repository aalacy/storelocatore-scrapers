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

base_url = 'https://bellagreen.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

def get_value(item):
    item = validate(item)
    if item == '' or item == 'N/A':
        item = '<MISSING>'    
    return item

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
            zipcode = addr[0]
        elif addr[1] == 'StateName':
            state = addr[0]
        else:
            street += addr[0].replace(',', '') + ' '

    return { 
            'street': get_value(street), 
            'city' : get_value(city), 
            'state' : get_value(state), 
            'zipcode' : get_value(zipcode)
            }

def fetch_data():
    output_list = []
    url = "https://bellagreen.com/restaurant-locations/"
    driver.get(url)
    source = driver.page_source
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="locations-wrapper"]//div[@class="location"]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        #print(get_value(store.xpath('.//h4[@class="location-name"]//text()')))
        output.append(get_value(store.xpath('.//h4[@class="location-name"]//text()'))) #location name
        detail = eliminate_space(store.xpath('.//p[@class="location-contact small"]//a//text()'))  
        #print(detail)      
        if len(detail) < 2:
            detail=eliminate_space(store.xpath('.//p[@class="location-contact small"]//text()'))
        address = parse_address(detail[0])
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        try:
            output.append(detail[1]) #phone
        except:
            output.append("<MISSING>")
        output.append('Bellagreen Restaurants') #location type
        output.append(get_value(store.xpath('.//h4[@class="location-name"]//@data-lat'))) #latitude
        output.append(get_value(store.xpath('.//h4[@class="location-name"]//@data-long'))) #longitude
        store_hours = eliminate_space(store.xpath('.//div[@class="location-hours"]//text()'))
        output.append(' '.join(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
