import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://gandolfosdeli.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

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
        if item != '' and item != '#':
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
    url = "https://gandolfosdeli.com/locations/"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    state_list = eliminate_space(response.xpath('//area/@href'))
    history = []
    for state in state_list:
        if state not in history:
            history.append(state)
            state_page = etree.HTML(session.get(state).text)
            store_list = state_page.xpath('.//ul[@class="store-info"]')[1:]            
            for store in store_list:
                store_link = validate(store.xpath('.//li[@class="store-sub shslong"]//a/@href'))
                output = []
                output.append(base_url) # url
                output.append(validate(store.xpath('.//li[@class="store-sub shslong"]//text()'))) #location name
                address = ', '.join(eliminate_space(store.xpath('.//li[@class="store-sub shlong"]//text()')))
                address = parse_address(address)
                output.append(address['street']) #address
                output.append(address['city']) #city
                output.append(address['state']) #state
                output.append(address['zipcode']) #zipcode   
                output.append('US') #country code
                output.append(validate(store_link.split('=')[-1])) #store_number
                output.append(validate(store.xpath('.//li[@class="store-sub shmed"]')[0].xpath('.//text()'))) #phone
                output.append("Gandolfo's Deli New York Delicatessen (Gandolfos) Sandwiches") #location type
                details = etree.HTML(session.get(store_link).text)
                output.append("<INACCESSIBLE>") #latitude
                output.append("<INACCESSIBLE>") #longitude
                output.append(get_value(eliminate_space(details.xpath('.//span[@class="storehours"]//text()')))) #opening hours
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
