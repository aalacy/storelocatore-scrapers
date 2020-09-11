import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://lebanesetaverna.com'

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
        if item != '' and 'Phone' not in item and 'Address' not in item and 'Hours' not in item:
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
    url = "https://lebanesetaverna.com/restaurant-locations/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//a[@class="restaurant-location-tile-link"]/@href')
    for link in store_list:        
        store = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h1[@class="entry-title"]/text()')))  #location name
        address = eliminate_space(store.xpath('.//div[@class="medium-6 columns small-text-center medium-text-right"]//a[2]//text()'))
        if len(address) > 2:
            output.append(validate(address[:-1])) #address
            address = validate(address[-1]).replace(',', '').split(' ')
            output.append(get_value(address[:-2])) #city
            output.append(address[-2]) #state
            output.append(address[-1]) #zipcode
        else:
            address = parse_address(get_value(address))
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//div[@class="medium-6 columns small-text-center medium-text-right"]//a[1]//text()'))) #phone
        output.append("Lebanese Restaurant - Best Mediterranean Cuisine") #location type
        output.append("<INACCESSIBLE>") #latitude
        output.append("<INACCESSIBLE>") #longitude
        store_hours = eliminate_space(store.xpath('.//div[@class="medium-6 columns small-text-center medium-text-left"]//text()'))
        output.append(validate(store_hours)) #opening hours 
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
