import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://zoomerzstores.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "https://zoomerzstores.com/locations?radius=-1&filter_catid=0&limit=0&filter_order=distance"
    session = requests.Session()
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': '32edeb25dad71c1c7dc8fbebd9de5d86=590499051483b07550207aad0c0b1b80; nrid=69257523a762df8d',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    formdata = {
        'searchzip': 'los angeles',
        'task': 'search',
        'radius': '-1',
        'option': 'com_mymaplocations',
        'limit': '0',
        'component': 'com_mymaplocations',
        'Itemid': '223',
        'zoom': '9',
        'format': 'json',
        'geo': '',
        'limitstart': '0',
        'latitude': '',
        'longitude': ''
    }
    request = session.post(url, headers=headers, data=formdata)
    store_list = json.loads(request.text)['features']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['properties']['name'])) #location name
        address = ', '.join(eliminate_space(etree.HTML(store['properties']['fulladdress']).xpath('.//text()'))[:-2]).replace('United States', '')
        address = parse_address(address)
        output.append(address['street']) #address
        if address['state'] != '<MISSING>':
            output.append(address['city']) #city
            output.append(address['state']) #state
        else:
            output.append(validate(address['city'].split(' ')[:-1])) #city
            output.append(validate(address['city'].split(' ')[-1])) #state
        output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append(get_value(store['id'])) #store_number
        output.append('<MISSING>') #phone
        output.append('Zoomerz Stores') #location type
        output.append(get_value(store['geometry']['coordinates'][0])) #latitude
        output.append(get_value(store['geometry']['coordinates'][1])) #longitude
        output.append('<MISSING>') #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
