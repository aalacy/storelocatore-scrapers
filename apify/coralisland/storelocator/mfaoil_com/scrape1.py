import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.mfaoil.com'


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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.mfaoil.com/portals/_default/skins/mfa%20oil/stores-2.txt"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)['Stores']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['LocationName'])) #location name
        output.append(get_value(store['AddressLine1'])) #address
        output.append(get_value(store['City'])) #city
        output.append(get_value(store['State'])) #state
        output.append(get_value(store['Zipcode'])) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['PhoneNumber'])) #phone
        output.append(get_value(store['Cateogry'])) #location type
        output.append(get_value(store['Latitude'])) #latitude
        output.append(get_value(store['Longitude'])) #longitude
        output.append('<MISSING>') #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
