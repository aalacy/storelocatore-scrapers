import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.stellabarra.com'

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
    url = "https://www.stellabarra.com"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//a[@class="btn btn-white"]/@href')
    for store_link in store_list:
        store = etree.HTML(session.get(store_link).text)
        details = eliminate_space(store.xpath('.//div[@class="one-third one-third-centered mobile-home-hide"]//text()'))
        output = []
        address = details[2].strip().split(',')
        output.append(base_url) # url
        output.append(address[0]) #location name
        output.append(details[1]) #address
        output.append(address[0]) #city
        output.append(address[1]) #state
        output.append('<MISSING>') #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(details[4]) #phone
        output.append("Stella Barra Pizzeria") #location type
        geo_loc = validate(store.xpath('.//div[@class="one-third one-third-centered mobile-home-hide"]//a/@href')).split('/@')[1].split(',17z')[0].split(',')
        output.append(geo_loc[0]) #latitude
        output.append(geo_loc[1]) #longitude
        store_hours = eliminate_space(store.xpath('.//div[@class="one-third hours-third one-third-centered mobile-home-hide"]//text()'))
        output.append(get_value(store_hours[1:])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
