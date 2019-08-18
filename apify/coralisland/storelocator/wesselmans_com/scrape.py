import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://wesselmans.com'

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
    url = "http://wesselmans.com/locations/"
    session = requests.Session()
    request = session.get(url)        
    response = etree.HTML(request.text)
    lat_list = request.text.split("['lat'] = ")[1:]
    lng_list = request.text.split("['long'] = ")[1:]
    store_list = response.xpath('.//section[@class="av_textblock_section  av-medium-hide av-small-hide av-mini-hide"]')
    for idx, store in enumerate(store_list):
        store = eliminate_space(store.xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(store[0]) #location name
        output.append(store[1]) #address
        address = store[2].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[4]) #phone
        output.append("Wesselman's") #location type
        lat = lat_list[idx].split(";\nav_google_map['0']")[0]
        lng = lng_list[idx].split(";\nav_google_map['0']")[0]
        output.append(lat) #latitude
        output.append(lng) #longitude
        output.append(store[6]) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
