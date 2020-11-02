import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://teahousebeverage.com'


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
    url = "http://teahousebeverage.com/locations/"
    session = requests.Session()
    request = session.get(url).text
    source = validate(request.split('wpgmaps_localize_marker_data = ')[1].split('var wpgmaps_localize_cat_ids')[0])[:-1]
    store_list = json.loads(source)['1']
    for key, store in list(store_list.items()):
        output = []
        output.append(base_url) # url
        output.append(get_value(store['title'])) #location name
        address = parse_address(validate(store['address']).replace('<br />', ','))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode   
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        detail = eliminate_space(etree.HTML(validate(store['desc'])).xpath('.//text()'))
        if len(detail) == 1:
            output.append('<MISSING>') #phone
        else:
            output.append(detail[0]) #phone
        output.append('The Teahouse - Tapioca & Tea') #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['lng'])) #longitude
        if len(detail) == 1:
            if 'coming' not in validate(detail).lower():
                output.append('<MISSING>') #opening hours          
                output_list.append(output)
        else:
            output.append(get_value(detail[1:]).replace(validate(store['address']), '')) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
