import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.lukeslobster.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
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
    url = "https://www.lukeslobster.com/locations"
    session = requests.Session()
    source = session.get(url).text
    data = validate(source.split('locations: ')[1].split('apiKey:')[0])[:-1]
    store_list = json.loads(data)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['name'])) #location name
        output.append(get_value(store['street'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        output.append(get_value(store['postal_code'])) #zipcode
        output.append('US') #country code
        output.append(get_value(store['id'])) #store_number
        output.append(get_value(store['phone_number'])) #phone
        output.append("Luke's Lobster | Traceable, Sustainable Seafood") #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['lng'])) #longitude
        store_hours = ''
        if store['hours'] != "":
            store_hours = eliminate_space(etree.HTML(store['hours']).xpath('.//text()'))
        output.append(get_value(store_hours)) #opening hours
        if float(store['lng']) < 0 and get_value(store_hours) != 'Permanently Closed':            
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
