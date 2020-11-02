import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://asianfoodmarkets.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\r', '').replace('\t', '').replace('\n', '').strip()

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
    url = "http://asianfoodmarkets.com"
    session = requests.Session()
    request = session.get(url)
    source = request.text
    store_list = validate(source.split('var infoWindowContent = [')[1].split('// Display multiple')[0]).replace("'", '').replace('+', '')[1:-3].split('],[')
    geo_list = validate(source.split('var markers = [')[1].split('];')[0])[1:-1].split('],[')
    for idx, store in enumerate(store_list):
        store = eliminate_space(etree.HTML(store).xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(store[0]) #location name
        address = parse_address(store[1])
        output.append(address['street']) #address        
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(validate(store[2].replace('Tel:', ''))) #phone
        output.append("Asian Grocery Stores") #location type
        geo = eliminate_space(geo_list[idx].split(','))
        output.append(geo[1]) #latitude
        output.append(geo[2]) #longitude
        output.append(', '.join(store[4:-1])) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
