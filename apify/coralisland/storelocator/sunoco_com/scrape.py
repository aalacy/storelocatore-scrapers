import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress



base_url = 'https://www.sunoco.com'

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
    with open('./cities.json') as data_file:    
        city_list = json.load(data_file)  
    url = "https://www.sunoco.com/api-set-station-list"
    page_url = ''
    session = requests.Session()
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json;charset=UTF-8',
        'Cookie': 'TS015f33b8=019de3c5d95cc087f070511e0f53a3c10c41dcccd398fd4a81c563ea5ae2066353deac5dca',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'
    }
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for city in city_list:
            payload = {
                'aplus': False,
                'atm': False,
                'autorepair': False,
                'carwash': False,
                'diesel': False,
                'kerosene': False,
                'lat': validate(city['latitude']),
                'lng': validate(city['longitude']),
                'rad': '100'
            }
            request = session.post(url, headers=headers, data=json.dumps(payload))
            data = json.loads(request.text)['payload']
            store_list = json.loads(data)['results']
            for store in store_list:
                store_id = validate(store['facility_id'])
                if store_id not in history:
                    history.append(store_id)
                    output = []
                    output.append(base_url) # url
                    store_link = 'https://www.sunoco.com/find-a-station/station/'+store_id
                    output.append(store_link) # page url
                    output.append(get_value(store['store_name']) + ' #' + store_id) #location name
                    output.append(get_value(store['street_address'])) #address
                    output.append(get_value(store['city'])) #city
                    output.append(get_value(store['state'])) #state
                    output.append(get_value(store['postalcode'])) #zipcode
                    output.append('US') #country code
                    output.append(get_value(store_id)) #store_number
                    phone = validate(store['phone'])
                    if phone == '0':
                        phone = ''
                    output.append(get_value(phone)) #phone
                    output.append('Sunoco Gas Stations') #location type
                    output.append(get_value(store['latitude'])) #latitude
                    output.append(get_value(store['longitude'])) #longitude
                    store_hours = ''
                    if store['opening_hours'] != None:
                        store_hours = store['opening_hours'][:2] + ':' + store['opening_hours'][2:] + '-' + store['closing_hours'][:2] + ':' + store['closing_hours'][2:]
                        if store_hours == '-':
                            store_hours = ''
                        if store_hours == '00:00-00:00' or store_hours == '00:00-24:00':
                            store_hours = '24hrs'
                    output.append(get_value(store_hours)) #opening hours
                    writer.writerow(output)

fetch_data()
