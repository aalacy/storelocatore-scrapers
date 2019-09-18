import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://littlegreekfreshgrill.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "https://littlegreekfreshgrill.com"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@id="box_second_half"]//a/@href')
    for store_link in store_list:
        store = etree.HTML(session.get(store_link).text)
        output = []
        output.append(base_url) # url
        address = eliminate_space(store.xpath('.//div[@id="store_address_info"]//text()'))
        output.append(address[0]) #location name
        output.append(address[1]) #address
        address = address[2].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append('<MISSING>') #phone
        output.append("Little Greek Fresh Grill") #location type
        output.append("<IINACCESSIBLE>") #latitude
        output.append("<IINACCESSIBLE>") #longitude
        store_hours = eliminate_space(store.xpath('.//div[@id="store_hours_of_operation"]//text()'))
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
