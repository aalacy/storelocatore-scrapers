import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://redoliverestaurant.com'

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
    url = "http://redoliverestaurant.com/red-olive-restaurant-locations-gallery/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="et_pb_text_inner"]')
    for store in store_list:
        link = validate(store.xpath('.//a/@href'))
        detail = etree.HTML(session.get(link).text)
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
        phone = get_value(detail.xpath('.//a[@class="fl r-i3pE_opxS6_w"]//text()'))
        output.append(phone) #phone
        output.append("Red Olive Restaurants") #location type
        output.append(get_value(detail.xpath('//div[@class="et_pb_map"]/@data-center-lat'))) #latitude
        output.append(get_value(detail.xpath('//div[@class="et_pb_map"]/@data-center-lng'))) #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
