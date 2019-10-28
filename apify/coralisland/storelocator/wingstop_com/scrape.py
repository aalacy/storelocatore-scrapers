import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress
import datetime


base_url = 'https://www.wingstop.com'


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
    with open('cities.json') as data_file:    
        city_list = json.load(data_file)  
    today = datetime.datetime.utcnow()
    startDateTime = today.strftime("%Y%m%d")
    tomorrow = today + datetime.timedelta(7)
    endDateTime = datetime.datetime.strftime(tomorrow,'%Y%m%d')
    page_url = 'https://www.wingstop.com/order'
    session = requests.Session()
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for city in city_list:
            url = 'https://api.wingstop.com/restaurants/near?lat='+str(city['latitude'])+'&long='+str(city['longitude'])+'&radius=500&limit=500&nomnom=calendars&nomnom_calendars_from='+startDateTime+'&nomnom_calendars_to='+endDateTime
            request = session.get(url)
            store_list = json.loads(request.text)['restaurants']
            for store in store_list:
                if get_value(store['id']) not in history:
                    history.append(get_value(store['id']))
                    output = []
                    output.append(base_url) # url
                    output.append(page_url) # page url
                    output.append(get_value(store['name'])) #location name
                    output.append(get_value(store['streetaddress'])) #address
                    output.append(get_value(store['city'])) #city
                    output.append(get_value(store['state'])) #state
                    output.append(get_value(store['zip'])) #zipcode
                    output.append(get_value(store['country'])) #country code
                    output.append(get_value(store['id'])) #store_number
                    output.append(get_value(store['telephone'])) #phone
                    output.append(get_value(store['storename'])) #location type
                    output.append(get_value(store['latitude'])) #latitude
                    output.append(get_value(store['longitude'])) #longitude
                    store_hours = []
                    if 'calendars' in store and len(store['calendars']['calendar']) > 0:                    
                        for hour in store['calendars']['calendar'][0]['ranges']:
                            start = validate(hour['start']).split(' ')[-1]
                            end = validate(hour['end']).split(' ')[-1]
                            if end == '00:00':
                                end = 'midnight'
                            store_hours.append(validate(hour['weekday']) + ' ' + start + '-' + end)
                    output.append(get_value(store_hours)) #opening hours        
                    # output_list.append(output)
                    writer.writerow(output)

fetch_data()
