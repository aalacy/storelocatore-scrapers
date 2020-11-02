import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://charleys.com'


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
    item = validate(item).replace('"', '').replace('<br />', ', ')
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
    url = "https://charleys.com/storelocator/charleys.csv"
    page_url = 'https://charleys.com/stores'
    session = requests.Session()
    request = session.get(url)
    store_list = request.text.split('\n')
    for store in store_list[1:]:        
        store = store.split('","')
        output = []
        output.append(base_url) # url
        output.append(page_url) # page url
        output.append(get_value(store[1])) #location name
        output.append(get_value(store[2])) #address
        output.append(get_value(store[3])) #city
        output.append(get_value(store[4])) #state        
        if get_value(store[5]) != '<MISSING>':
            ca_zip = get_value(re.findall("^[ABCEGHJKLMNPRSTVXY]{1}\d{1}[A-Z]{1} *\d{1}[A-Z]{1}\d{1}$", get_value(store[5])))
            output.append(get_value(store[5])) #zipcode
            country = 'US'
            if ca_zip != '<MISSING>':
                country = 'CA'
            if ca_zip == '<MISSING>' and len(get_value(store[4])) > 2:
                continue
            output.append(country)
            output.append(get_value(store[0])) #store_number
            output.append(get_value(store[6])) #phone
            output.append('Charleys Stores') #location type
            output.append(get_value(store[7])) #latitude
            output.append(get_value(store[8])) #longitude
            output.append(get_value(store[9])) #opening hours
            output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
