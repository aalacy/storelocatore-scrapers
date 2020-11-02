import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://pecksmarket.shoptocook.com'

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
    url = "http://pecksmarket.shoptocook.com/locations/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    title_list = response.xpath('//div[@class="entry-content"]//h2')
    store_list = response.xpath('//div[@class="entry-content"]//p')
    for idx, title in enumerate(title_list):
        output = []
        output.append(base_url) # url
        output.append(get_value(title.xpath('.//text()'))) #location name
        detail = eliminate_space(store_list[idx*4+1].xpath('.//text()'))
        output.append(', '.join(detail[:-3])) #address
        address = detail[-3].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(detail[-1]) #phone
        output.append("Peck's Markets") #location type
        geolocation = validate(store_list[idx*4+3].xpath('.//a/@href')).split('&ll=')[1].split('&spn')[0].split(',')
        output.append(geolocation[0]) #latitude
        output.append(geolocation[1]) #longitude
        store_hours = eliminate_space(store_list[idx*4+2].xpath('.//text()'))
        output.append(' '.join(store_hours[1:])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
