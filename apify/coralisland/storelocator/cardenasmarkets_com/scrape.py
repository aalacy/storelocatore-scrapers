import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://cardenasmarkets.com'


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
    url = "https://momentfeed-prod.apigee.net/api/llp.json?auth_token=PVNACVHMHURQFNUF&center=37.3053,-113.6706&multi_account=false&pageSize=500"    
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)    
    for store in store_list:
        output = []
        page_url = 'https://locations.cardenasmarkets.com' + get_value(store['llp_url'])
        store = store['store_info']
        output.append(base_url) # url
        output.append(page_url) # page url
        output.append(get_value(store['name'])) #location name
        output.append(get_value(store['address'])) #address
        output.append(get_value(store['locality'])) #city
        output.append(get_value(store['region'])) #state
        output.append(get_value(store['postcode'])) #zipcode
        output.append(get_value(store['country'])) #country code
        output.append(get_value(store['corporate_id'])) #store_number
        output.append(get_value(store['phone'])) #phone
        output.append('Cardenas Markets') #location type
        output.append(get_value(store['latitude'])) #latitude
        output.append(get_value(store['longitude'])) #longitude
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        store_hours = []
        hours = eliminate_space(validate(store['store_hours']).split(';'))
        for hour in hours:
            hour = hour.split(',')            
            temp = days_of_week[int(hour[0])-1] + ' ' + hour[1][:2] + ':' + hour[1][2:] + '-' + hour[2][:2] + ':' + hour[2][2:]
            store_hours.append(temp)
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
