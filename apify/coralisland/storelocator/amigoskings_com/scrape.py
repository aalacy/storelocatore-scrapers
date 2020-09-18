import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.amigoskings.com'

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
    url = "https://www.amigoskings.com/locations"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="views-field views-field-nodefield"]')
    for store in store_list:        
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h2[@class="nodeTitleCopy"]//text()'))) #location name
        output.append(get_value(store.xpath('.//div[@class="street-address"]//text()'))) #address        
        output.append(get_value(store.xpath('.//span[@class="locality"]//text()'))) #city
        output.append(get_value(store.xpath('.//span[@class="region"]//text()'))) #state
        output.append(get_value(store.xpath('.//span[@class="postal-code"]//text()'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//div[@class="tel"]//span[@class="value"]//text()'))) #phone
        output.append("Amigos/Kings Classic - Mexican and American Foods") #location type
        geo = get_value(store.xpath('.//div[@class="field-amigos-directions"]//a/@href')).split('addr=')[1].split(',')
        output.append(geo[0]) #latitude
        output.append(geo[1]) #longitude
        store_hours = eliminate_space(store.xpath('.//div[contains(@class, "group-hours field-group-div")]//text()'))
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
