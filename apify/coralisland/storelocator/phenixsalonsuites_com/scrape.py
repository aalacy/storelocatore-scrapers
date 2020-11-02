import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://phenixsalonsuites.com'


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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://phenixsalonsuites.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=400ae84e4e&load_all=1&layout=1"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['title'])) #location name
        output.append(get_value(store['street'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        output.append(get_value(store['postal_code'])) #zipcode
        output.append(get_value(store['country'])) #country code
        if 'united states' in get_value(store['country']).lower() or 'us' in get_value(store['country']).lower():
            output.append('<MISSING>') #store_number
            output.append(get_value(store['phone'])) #phone
            output.append('Phenix Salon Suites') #location type
            output.append(get_value(store['lat'])) #latitude
            output.append(get_value(store['lng'])) #longitude
            store_hours = validate(store['open_hours']).replace('"', '').replace('[', '').replace(']', '').replace('{', '').replace('}', '')
            output.append(get_value(store_hours)) #opening hours
            if 'coming' not in get_value(store['title']).lower():
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
