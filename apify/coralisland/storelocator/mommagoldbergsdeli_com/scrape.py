import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.mommagoldbergsdeli.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip().replace('\r', '').replace('\n', '')

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.mommagoldbergsdeli.com/location-results/?all=1"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@id="map_search mapsizer"]//div[@class="result"]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//div[@class="result_name"]//h3//text()'))) #location name
        detail = eliminate_space(store.xpath('.//div[@class="result_address"]//text()'))
        output.append(detail[0]) #address
        address = detail[1].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//div[@class="result_phone"][1]/text()'))) #phone
        output.append("Momma Goldberg's Deli") #location type
        output.append("<INACCESSIBLE>") #latitude
        output.append("<INACCESSIBLE>") #longitude
        output.append(get_value(store.xpath('.//div[@class="result_phone"][2]/text()'))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
