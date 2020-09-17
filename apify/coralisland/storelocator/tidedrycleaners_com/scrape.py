import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.tidedrycleaners.com'


def validate(item):    
    if item == None:
        item = ''    
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == bool:
        item = ''
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
    url = "https://www.tidedrycleaners.com/locations"
    session = requests.Session()
    request = session.get(url)
    source = validate(etree.HTML(request.text).xpath('.//div[@class="map mapbox mapboxgl-map"]/@data-source'))
    store_list = json.loads(source)['features']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['properties']['title'])) #location name
        output.append(get_value(store['properties']['street1'])) #address
        output.append(get_value(store['properties']['city'])) #city
        output.append(get_value(store['properties']['state'])) #state
        output.append(get_value(store['properties']['zip'])) #zipcode
        output.append('US') #country code
        output.append(get_value(store['properties']['id'])) #store_number
        output.append(get_value(store['properties']['phone'])) #phone
        output.append('Tide Dry Cleaners') #location type
        output.append(get_value(store['geometry']['coordinates'][0])) #latitude
        output.append(get_value(store['geometry']['coordinates'][1])) #longitude
        output.append(get_value(store['properties']['hours']).replace('<br />', ', ')) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
