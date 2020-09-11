import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.dollarstore.ca'

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.dollarstore.ca/store-locator/"
    session = requests.Session()
    request = session.get(url)
    source = validate(request.text.split('var wpgmaps_localize_marker_data = ')[1].split('var wpgmaps_localize_global_settings')[0])[:-1]
    store_list = json.loads(source)
    for key, store in list(store_list.items()):
        output = []
        output.append(base_url) # url
        output.append(get_value(store['title'])) #location name
        address = get_value(store['address']).split(',')
        output.append(get_value(address[:-3])) #address
        output.append(get_value(address[-3])) #city
        output.append(get_value(address[-2])) #state
        output.append(get_value(address[-1])) #zipcode
        output.append('CA') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['desc'])) #phone
        output.append('Dollar Store') #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['lng'])) #longitude
        output.append('<MISSING>') #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
