import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.grabbagreen.com'

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
    url = "https://locator.kahalamgmt.com/locator/index.php?brand=34&mode=map&latitude=37.09024&longitude=-95.712891&q=&pagesize=0"
    session = requests.Session()
    source = session.get(url).text
    # with open('res.txt', 'wb') as f:
    #     f.write(source.encode('utf8'))
    data = source.split('$(document).ready(function() {')[1].split('})')[0]
    store_list = data.split('= {')
    for store in store_list[1:]:
        store = json.loads('{' + store.split('}')[0] + '}')
        output = []
        output.append(base_url) # url
        output.append(get_value(store['Name'])) #location name          
        output.append(get_value(store['Address'])) #address
        output.append(get_value(store['City'])) #city
        output.append(get_value(store['State'])) #state
        output.append(get_value(store['Zip'])) #zipcode
        output.append(get_value(store['CountryCode'])) #country code
        output.append(get_value(store['StoreId'])) #store_number
        output.append(get_value(store['Phone'])) #phone
        output.append('Grabbagreen | food healthy meals') #location type
        output.append(get_value(store['Latitude'])) #latitude
        output.append(get_value(store['Longitude'])) #longitude
        link = 'https://www.grabbagreen.com/stores/healthy-food-killeen/' + str(store['StoreId'])
        data = etree.HTML(session.get(link).text)
        store_hours = ', '.join(eliminate_space(data.xpath('.//div[@class="storeCol"]')[0].xpath('.//ul//li//text()')))
        if 'coming' not in get_value(store['StatusName']).lower():
            output.append(store_hours) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
