import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://flipperspizzeria.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\r\n', '').strip()

def get_value(item):
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
            zipcode = addr[0]
        elif addr[1] == 'StateName':
            state = addr[0]
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
    url = "https://flipperspizzeria.com/wp-json/wp/v2/posts?per_page=100"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['title']['rendered'])) #location name
        address = parse_address(get_value(store['acf']['map_address']['address']))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode'].replace(',', '')) #zipcode
        output.append('US') #country code
        output.append(str(store['id'])) #store_number
        output.append(get_value(store['acf']['phone_number'])) #phone
        output.append("Flippers Pizzeria") #location type
        output.append(get_value(store['acf']['map_address']['lat'])) #latitude
        output.append(get_value(store['acf']['map_address']['lng'])) #longitude
        output.append(get_value(validate(etree.HTML(store['acf']['hours']).xpath('.//text()')))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
