import csv
import re
import pdb
from lxml import etree
import json
import usaddress
from sgrequests import SgRequests

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').replace('\xa0', ' ').strip()

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
    session = SgRequests()
    output_list = []
    url = "http://www.xn--seorfish-e3a.com/locations/"
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="fl-rich-text"]')
    for store in store_list:
        store = eliminate_space(store.xpath('.//text()'))
        output = []
        details = eliminate_space(store[1].split('   '))
        output.append('senorfish.com') # url
        output.append(store[0]) #location name
        if len(details) != 5:
            address = parse_address(', '.join(details[:2]).replace('.', ''))
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode   
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(details[2]) #phone
        else:
            address = parse_address(', '.join(details[:2]).replace('.', ''))
            output.append(details[0]) #address
            address = eliminate_space(details[1].split(' '))
            output.append(validate(address[:-2])) #city
            output.append(address[-2][:2]) #state
            output.append(address[-2][2:]) #zipcode   
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(address[-1]) #phone
        output.append("SENOR FISH") #location type
        output.append("<INIACCESSIBLE>") #latitude
        output.append("<INIACCESSIBLE>") #longitude
        output.append(validate(details[-2:-1])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
