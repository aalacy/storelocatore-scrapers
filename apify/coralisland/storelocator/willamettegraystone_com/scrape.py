import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.willamettegraystone.com/'

def validate(item):    
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
    url = "https://www.willamettegraystone.com/where-to-buy.php"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="b-address"]')
    for store in store_list:
        flag = validate(store.xpath('./@style'))
        if flag == '':
            store = eliminate_space(store.xpath('.//text()'))
            output = []
            output.append(base_url) # url
            address_end_point = 0
            phone = '<MISSING>'
            store_hours = '<MISSING>'
            for idx, item in enumerate(store):
                if 'phone:' in item.lower():
                    phone = item.replace('Phone:', '')
                    address_end_point = idx
                if 'hours:' in item.lower():
                    store_hours = ', '.join(store[idx:]).replace('Hours:', '').replace('  ', '').replace('\n', ' ')
            store = store[:address_end_point]
            output.append(store[0]) #location name
            output.append(', '.join(store[1: address_end_point-1])) #address
            address = store[address_end_point-1].strip().split(',')
            output.append(address[0]) #city
            output.append(address[1].strip().split(' ')[0]) #state
            output.append(address[1].strip().split(' ')[1]) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(phone) #phone
            output.append("Willamette Graystone") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            output.append(store_hours) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
