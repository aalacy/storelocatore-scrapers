import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://tonysaccos.com'

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
    url = "https://tonysaccos.com/locations/"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="locationli"]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//span[@itemprop="name"]//text()'))) #location name
        address = validate(store.xpath('.//span[@itemprop="streetAddress"]//text()')).split(',')
        output.append(get_value(address[0])) #address
        address = get_value(address[1]).split(' ')
        output.append(validate(address[:-2])) #city
        output.append(address[-2]) #state
        output.append(address[-1]) #zipcode
        output.append('US') #country code
        output.append(get_value(store.xpath('./@data-id'))) #store_number
        output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
        output.append("Coal Oven Pizza | Tony Saccos") #location type
        geo_loc = validate(store.xpath('.//a[contains(@class, "directions button btn")]/@href')).split('dir/')[1].split('/')[0].split(',')
        output.append(geo_loc[0]) #latitude
        output.append(geo_loc[1]) #longitude
        output.append(validate(store.xpath('./meta[@itemprop="openingHours"]//@content')).replace('\r', ',')) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
