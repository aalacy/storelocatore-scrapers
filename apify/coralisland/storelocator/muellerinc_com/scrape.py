import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.muellerinc.com'

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
    url = "https://www.muellerinc.com/o/rest/mups/location/"
    page_url = ''
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        url_key = validate(store['urlKey'])
        store_link = 'https://www.muellerinc.com/o/rest/mups/location/'+url_key
        store_info = json.loads(session.get(store_link).text)
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(get_value(store_info['name'])) #location name
        output.append(get_value(store_info['addressline1'])) #address
        output.append(get_value(store_info['city'])) #city
        output.append(get_value(store_info['statecode'])) #state
        output.append(get_value(store_info['zipcode'])) #zipcode
        output.append('US') #country code
        output.append(get_value(store_info['locationId'])) #store_info_number
        output.append(get_value(store_info['branchPhones'][0]['branchphonenumber'])) #phone
        output.append('Steel Buildings, Metal Buildings, Metal Roofing - Mueller, Inc') #location type
        output.append(get_value(store_info['latitude'])) #latitude
        output.append(get_value(store_info['longitude'])) #longitude
        store_hours = eliminate_space(etree.HTML(validate(store_info['businesshourshtmltext'])).xpath('.//text()'))
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
