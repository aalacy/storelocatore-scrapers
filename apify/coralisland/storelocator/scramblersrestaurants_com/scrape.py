import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://scramblersrestaurants.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip().replace('&nbsp;', ', ')

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
    url = "https://scramblersrestaurants.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1570448240056"
    page_url = 'https://scramblersrestaurants.com/locations/'
    session = requests.Session()
    request = session.get(url)
    store_list = etree.HTML(request.text).xpath('.//store/item')    
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(page_url) # page url
        output.append(get_value(store.xpath('.//location//text()'))) #location name        
        details = eliminate_space(etree.HTML(validate(store.xpath('.//description//text()'))).xpath('.//text()'))
        address = parse_address(details[0])
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode 
        output.append('US') #country code
        output.append(get_value(store.xpath('.//storeId//text()'))) #store_number
        output.append(get_value(store.xpath('.//telephone//text()'))) #phone
        output.append('Scramblers | breakfast & lunch') #location type
        output.append(get_value(store.xpath('.//latitude//text()'))) #latitude
        output.append(get_value(store.xpath('.//longitude//text()'))) #longitude
        store_hours = details[1]
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
