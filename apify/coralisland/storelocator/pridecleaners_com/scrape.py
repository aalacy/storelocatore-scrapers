import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'http://www.pridecleaners.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "http://www.pridecleaners.com/api/locations?format=json"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)    
    store_hours = eliminate_space(etree.HTML(session.get('http://www.pridecleaners.com/locations').text).xpath('.//section[@class="store-hours"]//text()'))
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(store['name']) #location name
        output.append(get_value(store['address'])) #address
        output.append(store['city']) #city
        output.append(store['state']) #state
        output.append(store['zip']) #zipcode
        output.append('US') #country code
        output.append(store['store_number']) #store_number
        output.append(get_value(store['phone'])) #phone
        output.append("Pride Cleaners | Kansas City #1 Dry Cleaners") #location type
        output.append(str(store['latitude'])) #latitude
        output.append(str(store['longitude'])) #longitude        
        output.append(', '.join(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
