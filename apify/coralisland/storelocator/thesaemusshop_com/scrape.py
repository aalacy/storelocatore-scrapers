import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://thesaemusshop.com'

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
    url = "https://thesaemusshop.com"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)    
    title_list = eliminate_space(response.xpath('.//div[@class="panel-body"]')[0].xpath('./p//text()'))
    store_list = response.xpath('.//div[@class="panel-body"]')[0].xpath('.//ul')
    for idx, store in enumerate(store_list):        
        output = []
        geolocation = store.xpath('.//a/@href')[0].split('8m2!3d')[1].split('!4d')
        store = eliminate_space(store.xpath('.//text()'))
        output.append(base_url) # url
        output.append(title_list[idx]) #location name
        output.append(store[0].replace(',', '')) #address
        address = store[1].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[2].replace('+', '')) #phone
        output.append("THE SAEM US:GLOBAL ECO-K Beauty, Skin Care, Cosmetic, Makeup Products") #location type
        output.append(geolocation[0]) #latitude
        output.append(geolocation[1]) #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
