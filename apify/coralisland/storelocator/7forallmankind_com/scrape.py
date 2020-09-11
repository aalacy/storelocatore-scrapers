import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://www.7forallmankind.com'

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
            state += addr[0].replace(',', '') + ' '
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
    url = "https://www.7forallmankind.com/store-locator/"
    session = requests.Session()
    source = session.get(url).text
    data = source.split('var markers1 = ')[1].split('];')[0] + ']'
    data = re.sub(",(\w+):", r',"\1":',  data)
    data = re.sub("{(\w+):", r'{"\1":',  data)
    store_list = json.loads(data)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['name'])) #location name
        address = validate(etree.HTML(store['address']).xpath('.//text()')).replace(', United States. -', '')
        if 'canada' not in address.lower():
            address = parse_address(address)
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode
            output.append('US') #country code            
        else:
            address = address.split(',')
            output.append(validate(', '.join(address[:-3]))) #address
            output.append(validate(address[-3])) #city
            output.append(validate(address[-2])) #state
            output.append(validate(address[-1].split('-')[-1])) #zipcode
            output.append('CA') #country code
        output.append(get_value(store['storelocatorid'])) #store_number
        phone = ''
        if store['contact'] != '':
            try:
                phone = etree.HTML(store['contact']).xpath('.//text()')[-1]
            except:
                pdb.set_trace()
        output.append(get_value(phone)) #phone
        output.append('7 For All Mankind Official Store | Premium Denim') #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['lng'])) #longitude
        output.append('<MISSING>') #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
