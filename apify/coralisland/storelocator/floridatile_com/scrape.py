import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.floridatile.com'


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
    url = "https://www.floridatile.com/api/public/v1/"
    page_url = 'https://www.floridatile.com/store-locator/'
    session = requests.Session()
    init_response = session.get('https://www.floridatile.com/store-locator/')
    token = ''
    for cookie in init_response.cookies:
        try:
            token = cookie.value
        except:
            pass
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://www.floridatile.com',
        'Referer': 'https://www.floridatile.com/store-locator/',
        'Sec-Fetch-Mode': 'cors',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'X-CSRFToken': token
    }
    payload = {
        'action': 'location_search',
        'searchLocation': 'dallas',
        'searchMiles': '10000',
        'userLat': '34.0522342',
        'userLong': '-118.2436849'
    }
    request = session.post(url, headers=headers, data=json.dumps(payload))
    store_list = json.loads(request.text)['data']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(page_url) # page url
        output.append(get_value(store['name'])) #location name
        output.append(get_value(store['address'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        zipcode = eliminate_space(validate(store['full_address']).split(',')[-1].split(' '))[0]
        output.append(zipcode) #zipcode  
        output.append(get_value(store['country'])) #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['phone'])) #phone
        output.append(get_value(store['type'])) #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['long'])) #longitude
        store_hours = []
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
