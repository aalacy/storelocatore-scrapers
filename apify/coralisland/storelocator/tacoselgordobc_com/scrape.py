import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://tacoselgordobc.com'

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
    url = "http://tacoselgordobc.com/locations/"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="vc_row wpb_row vc_inner vc_row-fluid"]')
    for store in store_list:
        store = store.xpath('.//div[@class="wpb_column vc_column_container vc_col-sm-6"]')[1]
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h2//text()'))) #location name
        detail = eliminate_space(store.xpath('.//article//p//text()'))
        address = parse_address(detail[0])
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode   
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(detail[1])) #phone
        output.append("Tacos El Gordo - Now in California & Nevada") #location type        
        geo_loc = validate(store.xpath('.//a')[0].xpath('./@href')).split('@')
        if len(geo_loc) == 2:
            geo_loc = geo_loc[1].split('data')[0].split(',')        
            output.append(geo_loc[0]) #latitude
            output.append(geo_loc[1]) #longitude
        else:
            output.append('<INACCESSIBLE>') #latitude
            output.append('<INACCESSIBLE>') #longitude
        output.append(validate(detail[2:])) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
