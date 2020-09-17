import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://blarneycastleoil.com/lucky-louies-pizza'

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
            state = addr[0].replace(',', '') + ' '
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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "http://blarneycastleoil.com/ez-mart-promo/ez-mart-locations/"
    page_url = ''
    session = requests.Session()
    response = session.get(url).text
    source = response.split('var maplistScriptParamsKo = ')[1].split('};')[0] + '}'
    store_list = json.loads(source)['KOObject'][0]['locations']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(url) # page url
        output.append(validate(store['title'])) #location name
        address = ', '.join(eliminate_space(etree.HTML(validate(store['address'])).xpath('.//text()'))).replace('United States', '')
        address = parse_address(address)
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append("<MISSING>") #phone
        output.append("Lucky Louie's Pizza - Blarney Castle Oil") #location type
        output.append(validate(store['latitude'])) #latitude
        output.append(validate(store['longitude'])) #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
