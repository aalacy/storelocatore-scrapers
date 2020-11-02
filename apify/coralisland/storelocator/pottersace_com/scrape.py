import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://pottersace.com'

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
    url = "http://pottersace.com/page.asp?p=Store%20Locator"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//table')[-1].xpath('.//tr')
    for store in store_list:
        tds = store.xpath('.//td')
        if len(tds) > 2:
            output = []
            detail = validate(tds[4].xpath('.//a/@href'))
            output.append(base_url) # url
            output.append(validate(tds[0].xpath('.//text()'))) #location name
            address = detail.split('&q=')
            if len(address) > 1 :
                address = address[1].split('&')[0].replace('+', ' ').replace('%22', '')
            else:
                address = detail.split('/place/')[1].split('/')[0].replace('+', ' ').replace('%22', '')
            address = parse_address(address)
            output.append(validate(tds[1].xpath('.//text()'))) #address            
            if 'Smithville' in output[1]:
                output.append('Smithville') #city
                output.append('TN') #state
            else:
                output.append(address['city']) #city
                output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode   
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(validate(tds[3].xpath('.//text()'))) #phone
            output.append("Potters Ace Home Center") #location type
            geo_loc = detail.split('ll=')
            if len(geo_loc) > 1:
                geo_loc = geo_loc[1].split('&')[0].split(',')
                output.append(geo_loc[0]) #latitude
                output.append(geo_loc[1]) #longitude
            else:
                output.append('<INACCESSIBLE>') #latitude
                output.append('<INACCESSIBLE>') #longitude
            output.append("<MISSING>") #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
