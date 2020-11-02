import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://www.searshomeapplianceshowroom.com'


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
    url = "http://www.searshomeapplianceshowroom.com/appliance/services/StoreLocatorListAll.Service.ss?c=3721178&format=HAS&getStates=T&n=3"
    page_url = ''
    session = requests.Session()
    request = session.get(url)
    state_list = json.loads(request.text)['states']
    for state in state_list:
        state_link = 'http://www.searshomeapplianceshowroom.com/appliance/services/StoreLocatorListAll.Service.ss?c=3721178&format=HAS&n=3&state='+state
        store_list = json.loads(session.get(state_link).text)        
        for store in store_list:            
            output = []
            output.append(base_url) # url
            output.append(get_value(store['store_url'])) # page url
            output.append(get_value(store['display_name'])) #location name
            output.append(get_value(store['add_1'])) #address
            output.append(get_value(store['city'])) #city
            output.append(get_value(store['state_or_province'])) #state
            output.append(get_value(store['zip_or_postal_code'])) #zipcode
            output.append(get_value(store['country'])) #country code
            output.append(get_value(store['name'])) #store_number
            output.append(get_value(store['phone'])) #phone
            output.append('Sears Home Appliance Showroom') #location type
            output.append(get_value(store['latitude'])) #latitude
            output.append(get_value(store['longitude'])) #longitude
            days_of_week = ['mon', 'tues', 'wed', 'thurs', 'fri', 'sat', 'sun']
            store_hours = []
            for day in days_of_week:
                open_day = 'open_' + day
                close_day = 'close_' + day
                hour = day + ' '
                if open_day in store:
                    hour += store[open_day] + '-'
                if close_day in store:
                    hour += store[close_day]
                store_hours.append(hour)
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
