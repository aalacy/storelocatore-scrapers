import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.westelm.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip()

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
    country_list = ['us', 'ca']
    url = "https://westelm.brickworksoftware.com/en/api/v3/stores"
    page_url = ''
    session = requests.Session()
    headers = {
        "Origin": "https://www.westelm.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    request = session.get(url)
    store_list = json.loads(request.text)['stores']
    for store in store_list:
        output = []
        if get_value(store['country_code']).lower() in country_list:
            output.append(base_url) # url            
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address_1'])) #address
            output.append(get_value(store['city'])) #city
            output.append(get_value(store['state'])) #state
            output.append(get_value(store['postal_code'])) #zipcode
            output.append(get_value(store['country_code'])) #country code
            output.append(get_value(store['number'])) #store_number
            output.append(get_value(store['phone_number'])) #phone
            output.append('Modern Furniture Store & Modern Home Decor Store') #location type
            output.append(get_value(store['latitude'])) #latitude
            output.append(get_value(store['longitude'])) #longitude
            store_hours = []
            for hour in store['regular_hours']:
                store_hours.append(validate(hour['display_day']) + ' ' + validate(hour['display_start_time']) + '-' + validate(hour['display_end_time']))
            if get_value(store['slug']) == 'scarsdale-at-vernon-hills':
                store_hours = 'Sun 11:00AM-6:00PM Mon-Sat 10:00AM-7:00PM'
            if len(store_hours) > 0:
                output.append(get_value(store_hours)) #opening hours
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
