import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.roscoeschickenandwaffles.com'

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
    url = "https://www.roscoeschickenandwaffles.com/locations-and-hours"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="col sqs-col-3 span-3"]//div[@class="sqs-block-content"]')
    for store in store_list:
        store = eliminate_space(store.xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(store[0]) #location name
        output.append(store[1]) #address
        output.append('<MISSING>') #city
        output.append('<MISSING>') #state
        output.append('<MISSING>') #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        phone = ''
        store_hours = ''
        if len(store) > 3:
            phone = store[2]
            store_hours = validate(store[4:])
        output.append(get_value(phone)) #phone
        output.append("Roscoe's House Of Chicken And Waffles") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(get_value(store_hours)) #opening hours
        if get_value(store_hours) != '<MISSING>':
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
