import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.weightwatchers.com'


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
    history = []
    with open('states.json') as data_file:    
        state_list = json.load(data_file)
    session = requests.Session()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    for state in state_list:
        url = "https://api1.weightwatchers.com/meetings/v1/locations?limit=1000000&locale=US&page=0&radius=1000&searchText="+state['abbreviation']
        page_url = ''
        request = session.get(url, headers=headers)
        store_list = json.loads(request.text)['locations']
        for store in store_list:
            output = []
            if get_value(store['id']) not in history:
                history.append(get_value(store['id']))
                page_url = base_url + '/us/find-a-meeting/'+get_value(store['id'])+'/'+get_value(store['slugTitleGeo'])
                output.append(base_url) # url
                output.append(page_url) # page url
                output.append(get_value(store['name'])) #location name
                output.append(get_value(store['address']['address1'])) #address
                output.append(get_value(store['address']['city'])) #city
                output.append(get_value(store['address']['state'])) #state
                output.append(get_value(store['address']['zipCode'])) #zipcode
                output.append(get_value(store['address']['country'])) #country code
                output.append(get_value(store['id'])) #store_number
                output.append('<MISSING>') #phone
                output.append('WW (Weight Watchers)') #location type
                output.append(get_value(store['address']['gpsCoordinates']['latitude'])) #latitude
                output.append(get_value(store['address']['gpsCoordinates']['longitude'])) #longitude
                store_hours = []    
                for hour in store['openHours']:
                    store_hours.append(validate(hour['meetingDay']['name']) + ' ' + validate(hour['meetingTime']).split('T')[-1] + '-' + validate(hour['meetingEndTime']).split('T')[-1])
                output.append(get_value(store_hours)) #opening hours
                output_list.append(output)        
    url = "https://api1.weightwatchers.ca/meetings/v1/locations?limit=1000000&locale=CA&page=0&radius=10000&searchText=QC"
    page_url = ''
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)['locations']
    for store in store_list:
        output = []
        if get_value(store['id']) not in history:
            history.append(get_value(store['id']))
            page_url = base_url + '/us/find-a-meeting/'+get_value(store['id'])+'/'+get_value(store['slugTitleGeo'])
            output.append(base_url) # url
            output.append(page_url) # page url
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address']['address1'])) #address
            output.append(get_value(store['address']['city'])) #city
            output.append(get_value(store['address']['state'])) #state
            output.append(get_value(store['address']['zipCode'])) #zipcode
            output.append(get_value(store['address']['country'])) #country code
            output.append(get_value(store['id'])) #store_number
            output.append('<MISSING>') #phone
            output.append('WW (Weight Watchers)') #location type
            output.append(get_value(store['address']['gpsCoordinates']['latitude'])) #latitude
            output.append(get_value(store['address']['gpsCoordinates']['longitude'])) #longitude
            store_hours = []    
            for hour in store['openHours']:
                store_hours.append(validate(hour['meetingDay']['name']) + ' ' + validate(hour['meetingTime']).split('T')[-1] + '-' + validate(hour['meetingEndTime']).split('T')[-1])
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
