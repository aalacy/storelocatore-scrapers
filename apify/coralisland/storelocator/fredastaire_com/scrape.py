import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.fredastaire.com'


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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.fredastaire.com/locations"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    request = session.get(url,headers=headers)
    source = request.text.split('("#map2").maps(')[1].split(').data')[0]
    store_list = json.loads(source)['places']
    for store in store_list:
        output = []
        if get_value(store['location']['country']) == 'United States':
            output.append(base_url) # url
            output.append(get_value(store['title'])) #location name        
            address = parse_address(store['address'].replace('USA', ''))
            output.append(address['street']) #address
            output.append(get_value(store['location']['city'])) #city
            output.append(get_value(store['location']['state'])) #state
            output.append(get_value(store['location']['postal_code'])) #zipcode
            output.append(get_value(store['location']['country'])) #country code
            output.append(get_value(store['id'])) #store_number
            if 'extra_fields' in store:
                output.append(get_value(store['extra_fields']['location-phone-number'])) #phone
            else:
                output.append('<MISSING>') #phone
            output.append('Fred Astaire Dance Studios') #location type
            output.append(get_value(store['location']['lat'])) #latitude
            output.append(get_value(store['location']['lng'])) #longitude
            output.append('<MISSING>') #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
