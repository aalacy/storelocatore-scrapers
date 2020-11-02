import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.cpk.com'


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
    history = []
    with open('cities.json') as data_file:    
        city_list = json.load(data_file)
    for city in city_list:
        url = "https://www.cpk.com/Location/StoreLocatorJs"
        session = requests.Session()
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': 'ARRAffinity=27bd506faff9f52762610c4a4969462a3120496a4ccb2eea29b0dffe46465858; MobileAlert=',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        payload = {
            'lat': validate(city['latitude']),
            'lng': validate(city['longitude']),
            'mapsize': '315205',
            'orderonline': 'false',
            'zoom': '12'
        }
        request = session.post(url, headers=headers, data=json.dumps(payload))        
        store_list = json.loads(request.text)
        for store in store_list:
            output = []
            store_id = get_value(store['ID'])
            if store_id not in history:
                history.append(store_id)
                output.append(base_url) # url
                page_url = 'https://www.cpk.com/Location/Details/'+get_value(store['UrlName'])
                output.append(page_url) # page url
                output.append(get_value(store['Name'])) #location name
                output.append(get_value(store['Address'])) #address
                output.append(get_value(store['City'])) #city
                output.append(get_value(store['State'])) #state
                output.append(get_value(store['ZipCode'])) #zipcode
                output.append(get_value(store['CountryCode'])) #country code
                output.append(store_id) #store_number
                output.append(get_value(store['PhoneNumber'])) #phone
                output.append('California Pizza Kitchen') #location type
                output.append(get_value(store['Latitude'])) #latitude
                output.append(get_value(store['Longitude'])) #longitude
                store_hours = validate(store['ScheduleDisplay'].replace('|', ', '))
                output.append(get_value(store_hours)) #opening hours
                output_list.append(output)                
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
