import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.bakerdist.com'


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


def fetch_data():
    output_list = []
    history = []
    url = "https://www.bakerdist.com/branch/service/locate/?address="
    page_url = 'https://www.bakerdist.com/store-locator/'
    session = requests.Session()
    with open('./cities.json') as data_file:    
        city_list = json.load(data_file)  
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for city in city_list:
            url = url + city['city'].replace(' ', '+')
            request = session.get(url)
            store_list = json.loads(request.text)['branches']
            for store in store_list:
                store_id = get_value(store['branch_id'])
                if store_id not in history:
                    history.append(store_id)                    
                    output = []
                    output.append(base_url) # url
                    output.append(page_url) # page url
                    output.append(get_value(store['branch_name'])) #location name
                    output.append(get_value(store['address']['address_1'])) #address
                    output.append(get_value(store['address']['city'])) #city
                    output.append(get_value(store['address']['region_code'])) #state
                    output.append(get_value(store['address']['postcode'])) #zipcode
                    output.append(get_value(store['address']['country'])) #country code
                    output.append(store_id) #store_number
                    output.append(get_value(store['phone'])) #phone
                    output.append('Baker Distributing') #location type
                    output.append(get_value(store['latitude'])) #latitude
                    output.append(get_value(store['longitude'])) #longitude
                    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    hours = store['formatted_hours']
                    store_hours = []
                    for key, hour in list(hours.items()):
                        store_hours.append(days_of_week[int(key)-1] + ' ' + validate(hour['open']) + '-' + validate(hour['close']))
                    output.append(get_value(store_hours)) #opening hours
                    writer.writerow(output)

fetch_data()