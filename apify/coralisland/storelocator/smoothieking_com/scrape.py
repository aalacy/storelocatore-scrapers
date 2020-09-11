import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://smoothieking.com'


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


def fetch_data():
    output_list = []
    history = []
    with open('cities.json') as data_file:    
        city_list = json.load(data_file)    
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])        
        for city in city_list:
            url = "https://momentfeed-prod.apigee.net/api/llp.json?auth_token=TLLLFMCOPXOWXFMY&center="+str(city['latitude'])+','+str(city['longitude'])+"&multi_account=false&page=1&pageSize=10000"
            session = requests.Session()
            request = session.get(url)
            store_list = json.loads(request.text)
            for store in store_list:
                store = store['store_info']
                output = []
                output.append(base_url) # url
                if get_value(store['corporate_id']) not in history:
                    history.append(get_value(store['corporate_id']))
                    output.append(get_value(store['name'])) #location name
                    output.append(get_value(store['address'])) #address
                    output.append(get_value(store['locality'])) #city
                    output.append(get_value(store['region'])) #state
                    output.append(get_value(store['postcode'])) #zipcode
                    output.append(get_value(store['country'])) #country code
                    output.append(get_value(store['corporate_id'])) #store_number
                    output.append(get_value(store['phone'])) #phone
                    output.append('Smoothie King') #location type
                    output.append(get_value(store['latitude'])) #latitude
                    store_hours = []
                    hours = eliminate_space(validate(store['hours']).split(';'))
                    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']        
                    for hour in hours:
                        hour = hour.split(',')
                        store_hours.append(days_of_week[int(hour[0])-1] + ' ' + hour[1][:2] + ':' + hour[1][2:] + '-' + hour[2][:2] + ':' + hour[2][2:])
                    output.append(get_value(store['longitude'])) #longitude        
                    output.append(get_value(store_hours)) #opening hours
                    writer.writerow(output)
                    # output_list.append(output)

def scrape():
    fetch_data()
    # write_output(data)

scrape()
