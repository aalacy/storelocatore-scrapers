import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.tuxedobysarno.com'


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
    url = "https://www.tuxedobysarno.com/wp-admin/admin-ajax.php"
    headers = {

    }
    formdata = {
        'postal_code': 'dallas',
        'distance': '10000',
        'lat': '32.7766642',
        'lng': '-96.79698789999998',
        'rad': '10000000',
        'action': 'get_stores'
    }
    session = requests.Session()
    request = session.post(url, headers=headers, data=formdata)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['dba'])) #location name
        output.append(get_value(store['address_1'] + ' ' + store['address_2'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        output.append(get_value(store['postcode'])) #zipcode
        if get_value(store['postcode']) == '00000':
            output.append('CA') #country code
        else:
            output.append('US') #country code
        output.append(get_value(store['store_id'])) #store_number
        output.append(get_value(store['phone'])) #phone
        output.append('Suits & Tuxedos to Rent or Purchase') #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['long'])) #longitude
        if store['store_hours']:
            store_hours = eliminate_space(etree.HTML(store['store_hours']).xpath('.//text()'))
        else:
            store_hours = "<MISSING>"
        output.append(validate(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
