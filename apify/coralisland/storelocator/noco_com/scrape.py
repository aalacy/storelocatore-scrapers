import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.noco.com'


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
    url = "https://www.noco.com/locator"
    page_url = ''
    session = requests.Session()
    request = session.get(url)
    source = validate(request.text.split('var locations = "')[1].split('";')[0]).replace('\\', '') 
    store_list = json.loads(source.replace('"{', '{').replace('}"', '}'))    
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(url) # page url
        output.append(get_value(store['Store Display Name'])) #location name
        output.append(get_value(store['Address'])) #address
        output.append(get_value(store['City'])) #city
        output.append(get_value(store['State'])) #state
        output.append(get_value(store['Zip Code'])) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['Phone Number'])) #phone
        output.append('NOCO Energy Corporation') #location type
        output.append('<MISSING>') #latitude
        output.append('<MISSING>') #longitude
        output.append(get_value(store['Business Hours'])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
