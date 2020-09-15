import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.brush32.com'


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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.brush32.com/dentist-offices/"
    page_url = ''
    session = requests.Session()
    request = session.get(url)
    source = validate(request.text.split('var map_data = ')[1].split('};')[0])+'}'
    store_list = json.loads(source)['offices']
    for key, store in list(store_list.items()):        
        output = []
        output.append(base_url) # url
        output.append(get_value(store['url'])) # page url
        output.append(get_value(store['full_name'])) #location name
        if 'Brush32' in get_value(store['full_name']):
            output.append(get_value(store['street_address'])) #address
            address = validate(store['city_state_zip']).split(', ')
            output.append(address[0]) #city
            output.append(address[1].strip().split(' ')[0]) #state
            output.append(address[1].strip().split(' ')[1]) #zipcode
            output.append('US') #country code
            output.append(get_value(store['ID'])) #store_number
            phone = ''
            if 'phone' in store:
                phone = store['phone']
            output.append(get_value(phone)) #phone
            output.append('Dentist Offices') #location type
            output.append(get_value(store['latitude'])) #latitude
            output.append(get_value(store['longitude'])) #longitude
            store_hours = []        
            if store['hours']:
                for key, value in list(store['hours'].items()):
                    store_hours.append(key + ' ' + validate(value).replace('&nbsp;&ndash;&nbsp;','-'))
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
