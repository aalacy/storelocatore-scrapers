import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.vilebrequin.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").replace('</br>', ' ').replace('\n', '').strip()

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
    url = "https://www.vilebrequin.com/eu/en/store-locator"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text.split('vbq.stores = ')[1].split('};')[0] + '}')
    for key, store in store_list.items():
        output = []
        if get_value(store['countryCode']) == 'US':
            output.append(base_url) # url
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address1'] + ' ' + store['address2'])) #address
            output.append(get_value(store['city'])) #city
            output.append(get_value(store['stateCode'])) #state
            output.append(get_value(store['postalCode'])) #zipcode
            output.append(get_value(store['countryCode'])) #country code
            output.append('<MISSING>') #store_number
            output.append(get_value(store['phone'])) #phone
            output.append('Vilebrequin Official Online Store') #location type
            output.append(get_value(store['latitude'])) #latitude
            output.append(get_value(store['longitude'])) #longitude
            store_hours = eliminate_space(etree.HTML(store['translatedStoreHoursDatetime']).xpath('.//text()'))
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
