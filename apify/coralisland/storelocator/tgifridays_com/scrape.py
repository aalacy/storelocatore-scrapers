import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://tgifridays.com'


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
    url = "https://locations.tgifridays.com/umbraco/api/locationservice/findlocations?lat=32.7763&lng=-96.7969&units=10000&distance=10000"
    session = requests.Session()
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)
    for store in store_list:        
        store = store['Result']
        output = []
        output.append(base_url) # url
        output.append('https://locations.tgifridays.com' + validate(store['Url'])) # page url
        output.append(get_value(store['LocationName'] + ' ' + store['DisplayName'])) #location name
        output.append(get_value(store['Address'])) #address
        output.append(get_value(store['City'])) #city
        output.append(get_value(store['State'])) #state
        output.append(get_value(store['ZipCode'])) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['PhoneNumber'])) #phone
        output.append('UsableNet Assistive Switch') #location type
        output.append(get_value(store['Latitude'])) #latitude
        output.append(get_value(store['Longitude'])) #longitude
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        store_hours = []
        for day in days_of_week:
            if store[day]['Closed'].lower() == 'false':
                if store[day]['Is24Hour'].lower() == 'false':
                    store_hours.append(validate(store[day]['DayName']) + ' ' + validate(store[day]['From']) + ' - ' + validate(store[day]['To']))
                else:
                    store_hours.append(validate(store[day]['DayName']) + ' 24hrs')
            else:
                store_hours.append(validate(store[day]['DayName']) + ' Closed')
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
