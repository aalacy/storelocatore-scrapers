import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.thetirechoice.com'


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
    url = "https://www.thetirechoice.com/wp-json/monro/v1/stores/brand?brand=8"
    page_url = 'https://www.thetirechoice.com/store-search/'
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)['data']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(page_url) # page url
        output.append(get_value(store['BrandDisplayName']) + '-' + get_value(store['City'])) #location name
        output.append(get_value(store['Address'])) #address
        output.append(get_value(store['City'])) #city
        output.append(get_value(store['StateCode'])) #state
        output.append(get_value(store['ZipCode'])) #zipcode
        output.append('US') #country code
        output.append(get_value(store['Id'])) #store_number
        output.append(get_value(store['SalesPhone'])) #phone
        output.append('The Tire Choice') #location type
        output.append(get_value(store['Latitude'])) #latitude
        output.append(get_value(store['Longitude'])) #longitude
        store_hours = []
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days_of_week:
            if day+'OpenTime' in store:
                hour = day + ' ' + validate(store[day+'OpenTime']) + '-' + validate(store[day+'CloseTime'])
                store_hours.append(hour)
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
