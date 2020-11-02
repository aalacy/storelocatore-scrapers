import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jimmassey_com')




base_url = 'http://www.jimmassey.com'


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
    url = "http://www.jimmassey.com/locations/"
    session = requests.Session()
    request = session.get(url).text
    source = validate(request.split('maplistScriptParamsKo = ')[1].split('};')[0]) + '}'
    store_list =json.loads(source)['KOObject'][0]['locations'] 
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['locationUrl'])) # page url
        output.append(get_value(store['title'])) #location name
        details = eliminate_space(etree.HTML(store['description']).xpath('.//text()'))
        phone = ''
        store_hours = []
        for idx, de in enumerate(details):
            if 'phone' in de.lower():
                phone = details[idx+1]
            if 'hour' in de.lower():
                store_hours = details[idx:]
        if phone == '':            
            phone = details[-1]
            store_hours = store_hours[:-1]
            address = validate(etree.HTML(store['address']).xpath('.//text()')).split(',')
            output.append(get_value(address[0].split(' ')[:-1])) #address
            output.append(address[0].split(' ')[-1]) #city
            output.append(address[1]) #state
            output.append('<MISSING>') #zipcode 
        else:
            address = validate(etree.HTML(store['address']).xpath('.//text()'))
            address = parse_address(address)
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode 
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(phone)) #phone
        output.append("Drycleaning Locations | Laundry and Drycleaning| Jim Massey's Cleaners") #location type
        output.append(get_value(store['latitude'])) #latitude
        output.append(get_value(store['longitude'])) #longitude        
        output.append(get_value(store_hours).replace('Hours:', '')) #opening hours
        logger.info(output)
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
