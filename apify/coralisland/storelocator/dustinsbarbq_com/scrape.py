import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://dustinsbarbq.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

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
    url = "http://dustinsbarbq.com/locations/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="su-column-inner su-clearfix"]')
    for store in store_list:
        store = eliminate_space(store.xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(store[0]) #location name
        output.append(store[1]) #address
        address = eliminate_space(store[2].strip().split(' '))
        output.append(validate(address[:-2]).replace(',', '')) #city
        output.append(address[-2]) #state
        output.append(address[-1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[3]) #phone
        output.append("Dustins Barbeque") #location type
        output.append("<INACCESSIBLE>") #latitude
        output.append("<INACCESSIBLE>") #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
