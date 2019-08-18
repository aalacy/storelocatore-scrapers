import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://liquidhighway.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "http://liquidhighway.com/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = eliminate_space(response.xpath('.//div[@class="left-cont"]//text()'))[2:]
    count = len(store_list) / 4
    for idx in range(0, count):
        idx = idx * 4    
        output = []
        output.append(base_url) # url
        output.append(get_value(store_list[idx+0][2:])) #location name
        output.append(get_value(store_list[idx+1])) #address
        address = get_value(store_list[idx+2]).split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store_list[idx+3].split(':')[1])) #phone
        output.append("Liquid Highway") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append("<MISSING>") #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
