import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.cat.com'


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
    session = requests.Session()
    history = []
    with open('./cities.json') as data_file:    
        city_list = json.load(data_file)
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': 'cat-ms.esri.com',
            'Origin': 'https://www.cat.com',
            'Referer': 'https://www.cat.com/en_US.html',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
        }
        for city in city_list:
            url = 'https://cat-ms.esri.com/dls/cat/locations/en?f=json&forStorage=false&distanceUnit=mi&&searchType=location&maxResults=100000&productDivId=1%2C6%2C3%2C5%2C4%2C8%2C7%2C2&serviceId=1%2C2%2C3%2C4%2C8%2C9%2C10%2C5%2C6%2C7%2C12&appId=n6HDEnXnYRTDAxFr&searchValue='+str(city['longitude'])+'%2C'+str(city['latitude'])
            page_url = ''
            request = session.get(url, headers=headers)
            store_list = json.loads(request.text)            
            if len(store_list) < 3:
                continue
            for store in store_list:                
                store_id = get_value(store['dealerLocationId'])
                if store_id not in history:
                    history.append(store_id)
                    output = []
                    output.append(base_url) # url
                    output.append('https://www.cat.com/en_US.html') # page url
                    output.append(get_value(store['dealerLocationName'])) #location name
                    output.append(get_value(store['siteAddress'])) #address
                    output.append(get_value(store['siteCity'])) #city
                    output.append(get_value(store['siteState'])) #state
                    output.append(get_value(store['sitePostal'])) #zipcode
                    output.append(get_value(store['countryCode'])) #country code
                    output.append(store_id) #store_number
                    output.append(get_value(store['locationPhone'])) #phone
                    output.append('Cat Product') #location type
                    output.append(get_value(store['latitude'])) #latitude
                    output.append(get_value(store['longitude'])) #longitude
                    store_hours = []
                    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    hours = store['stores'][0]
                    for day in days_of_week:
                        day_key = 'storeHours' + day
                        if day_key in hours:
                            time = validate(hours[day_key])
                            if time == '':
                                time = 'closed'
                            store_hours.append(day + ' ' + time)
                    output.append(get_value(store_hours)) #opening hours
                    writer.writerow(output)
                    
fetch_data()
