import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.aliceandolivia.com'

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
    url = "https://www.aliceandolivia.com/front/app/store/search?execution=e6s1"
    page_url = 'https://www.aliceandolivia.com/store-locator.html'
    session = requests.Session()
    source = session.get(url).text
    request = session.get(url)
    source = validate(request.text.split('var storeResult = ')[1].split('storeSearch')[0])[:-1]
    store_list = json.loads(source)['store']
    for store in store_list:
        store = store['store']
        country = get_value(store['address']['country'])
        if country == 'US':
            output = []
            output.append(base_url) # url
            output.append(page_url) # page url
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address']['address1'])) #address
            output.append(get_value(store['address']['city'])) #city
            output.append(get_value(store['address']['province'])) #state
            output.append(get_value(store['address']['postalCode'])) #zipcode
            output.append(country) #country code
            output.append(get_value(store['storeId'])) #store_number
            output.append(get_value(store['phoneNumber'])) #phone
            output.append(get_value(store['storeType'])) #location type
            output.append(get_value(store['latitude'])) #latitude
            output.append(get_value(store['longitude'])) #longitude
            store_hours = []
            if store['hours']:
                store_hours = get_value(eliminate_space(etree.HTML(store['hours']).xpath('.//text()')))
            if 'CLOSED FOR THE SEASON!' not in store_hours:
                output.append(store_hours) #opening hours
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
