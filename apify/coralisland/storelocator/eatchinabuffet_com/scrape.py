import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://eatchinabuffet.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "http://eatchinabuffet.com/locations/"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//table[@id="tablepress-1"]//tbody//tr')
    for store in store_list:
        store = eliminate_space(store.xpath('.//td//text()'))
        output = []
        output.append(base_url) # url
        output.append('<MISSING>') #location name
        output.append(store[1]) #address
        output.append(store[0]) #city
        output.append(store[3]) #state
        output.append(store[2]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[4]) #phone
        output.append("China Buffet Chinese Restaurant") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
