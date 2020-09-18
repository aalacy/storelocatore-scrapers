import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.chevronextramile.com'


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
    with open('./cities.json') as data_file:    
        city_list = json.load(data_file)
    url = "https://www.chevronextramile.com/en/FindStore/GetStations"
    session = requests.Session()
    page_url = 'https://www.chevronextramile.com/find-a-convenience-store'
    headers = {
       'Accept': '*/*',
       'Accept-Encoding': 'gzip, deflate, br',
       'Accept-Language': 'en-US,en;q=0.9',
       'Connection': 'keep-alive',
       'Content-Length': '204',
       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
       'Host': 'www.chevronextramile.com',
       'Origin': 'https://www.chevronextramile.com',
       'Referer': 'https://www.chevronextramile.com/find-a-convenience-store',
       'Sec-Fetch-Mode': 'cors',
       'Sec-Fetch-Site': 'same-origin',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
       'X-Requested-With': 'XMLHttpRequest'
    }
    for city in city_list:
        formdata = {
            'data[lat]': str(city['latitude']),
            'data[lng]': str(city['longitude']),
            'data[extramile]': '0',
            'data[beer]': '0',
            'data[carwash]': '0',
            'data[coffee]': '0',
            'data[diesel]': '0',
            'data[extra]': '0',
            'data[icee]': '0',
            'data[restroom]': '0',
        }
        request = session.post(url, data=formdata, headers=headers)
        store_list = json.loads(request.text)['stations']
        for store in store_list:
            uni_id = validate(store['lat']) + '-' + validate(store['lng'])
            if uni_id  not in history:
                history.append(uni_id)
                output = []
                output.append(base_url) # url
                output.append(page_url) # page url
                output.append(get_value(store['name'])) #location name
                output.append(get_value(store['address'])) #address
                output.append(get_value(store['city'])) #city
                output.append(get_value(store['state'])) #state
                output.append(get_value(store['zip'])) #zipcode
                output.append('US') #country code
                output.append(get_value(store['name'].split('#')[-1])) #store_number
                output.append(get_value(store['phone'])) #phone
                output.append('Chevron ExtraMile') #location type
                output.append(get_value(store['lat'])) #latitude
                output.append(get_value(store['lng'])) #longitude
                store_hours = []
                output.append(get_value(store_hours)) #opening hours
                output_list.append(output)                
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
