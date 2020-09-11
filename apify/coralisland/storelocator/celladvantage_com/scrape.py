import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'http://celladvantage.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

def get_value(item):
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
    url = "http://celladvantage.com/locations/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('.//div[@class="single-state-content"]//a/@href')
    for store in store_list:
        store = etree.HTML(session.get(store).text)
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h1[@class="alpha"]//text()'))) #location name
        detail = eliminate_space(store.xpath('.//span[@class="contact-content"]')[2].xpath('.//text()'))
        output.append(detail[0]) #address
        address = detail[1].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store.xpath('.//span[@class="contact-content"]')[0].xpath('.//text()'))) #phone
        output.append("U.S. Cellular Locations in the Midwest") #location type
        output.append('<INACCESSIBLE>') #latitude
        output.append('<INACCESSIBLE>') #longitude
        h_temp = []
        store_hours = store.xpath('.//table[@class="store-hours-table"]//tr')
        for hour in store_hours:
            hour = validate(hour.xpath('.//text()'))
            h_temp.append(hour)
        store_hours = ', '.join(h_temp)
        output.append(store_hours) #opening hour        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
