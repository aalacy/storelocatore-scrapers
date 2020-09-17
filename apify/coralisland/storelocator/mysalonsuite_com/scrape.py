import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://www.mysalonsuite.com'


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
    url = "https://easylocator.net/ajax/search_by_lat_lon/Weebly%20Hearts/32.7766642/-96.79698789999998/0/10000/null/null"
    page_url = ''
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)['physical']
    for store in store_list:
        if 'coming' not in get_value(store['street_address']).lower():
            output = []
            output.append(base_url) # url
            output.append(get_value(store['website_url'])) # page url
            output.append(get_value(store['name'])) #location name
            street = validate(store['street_address_line2'])
            if street == '':
                street = validate(store['street_address'])
            output.append(get_value(street)) #address
            output.append(get_value(store['city'])) #city
            output.append(get_value(store['state_province'])) #state
            output.append(get_value(store['zip_postal_code'])) #zipcode
            if validate(store['country']).lower() == 'canada':
                output.append('CA') #country code
            else:
                output.append('US') #country code
            output.append(get_value(store['location_number'])) #store_number
            output.append(get_value(store['phone'])) #phone
            output.append('Love the Suite Life') #location type
            output.append(get_value(store['lat'])) #latitude
            output.append(get_value(store['lon'])) #longitude
            store_hours = []
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
