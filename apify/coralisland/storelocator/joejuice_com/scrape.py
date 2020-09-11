import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.joejuice.com'


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
    url = "https://storerocket.global.ssl.fastly.net/api/user/KDB8e7W49M/locations?radius=50"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)['results']['locations']
    for store in store_list:
        output = []
        if 'united states' in get_value(store['country']).lower():
            output.append(base_url) # url
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address_line_1'] + ' ' + store['address_line_2'])) #address
            output.append(get_value(store['city'])) #city
            output.append(get_value(store['state'])) #state
            output.append(get_value(store['postcode'])) #zipcode
            output.append(get_value(store['country'])) #country code
            output.append(get_value(store['id'])) #store_number
            output.append(get_value(store['phone'])) #phone
            output.append('JOE & THE JUICE') #location type
            output.append(get_value(store['lat'])) #latitude
            output.append(get_value(store['lng'])) #longitude
            store_hours = []
            if store['hours']:
                for day, hour in list(store['hours'].items()):
                    hour = validate(hour)
                    if hour == '':
                        hour = 'closed'
                    store_hours.append(day + ' ' + hour)
            else:
                store_hours = "<MISSING>"
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
