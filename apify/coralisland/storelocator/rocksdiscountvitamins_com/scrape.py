import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://rocksdiscountvitamins.com'

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
    url = "https://rocksdiscountvitamins.com/find-a-location/"
    session = requests.Session()
    request = session.get(url)
    source = request.text
    store_list = json.loads(validate(source.split('var wpgmaps_localize_marker_data = ')[1].split('var wpgmaps_localize_cat_ids')[0])[:-1])['1']
    for key, store in list(store_list.items()):
        output = []        
        output.append(base_url) # url
        output.append(store['title']) #location name
        address = parse_address(store['address'].replace('USA', '').replace('United States', ''))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        detail = etree.HTML(store['desc']).xpath('.//p')
        phone = ''
        store_hours = ''
        if len(detail) >= 2:
            phone = eliminate_space(detail[0].xpath('.//text()'))[1]
            store_hours = eliminate_space(detail[1].xpath('.//text()'))[1:]
        output.append(get_value(phone)) #phone
        output.append("Rock's Discount Vitamins - Fuel Your Passion For Fitness") #location type
        output.append(store['lat']) #latitude
        output.append(store['lng']) #longitude
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
