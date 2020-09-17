import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://www.samsitalian.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
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
    url = "http://www.samsitalian.com/locations/"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="et_pb_section et_pb_section_1 et_pb_with_background et_section_regular"]//div[contains(@class, "et_pb_css_mix_blend_mode_passthrough")]')
    for store in store_list[1:]:
        store = eliminate_space(store.xpath('.//text()'))
        if len(store) > 3:
            output = []
            output.append(base_url) # url
            output.append(store[0]) #location name
            address = store[1].split(',')
            output.append(address[0]) #address        
            output.append(address[1]) #city
            output.append(address[2]) #state
            output.append('<MISSING>') #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(store[2].replace('Phone #:', '')) #phone
            output.append("Sam's Italian Foods") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            output.append(get_value(store[4:])) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
