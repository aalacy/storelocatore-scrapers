import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://tiosmexicanfood.com'

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
    url = "http://tiosmexicanfood.com"
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//li[@id="menu-item-231"]//li//a/@href')
    for store_link in store_list:
        store = session.get(store_link, headers=headers).text
        output = []
        details = eliminate_space(etree.HTML(store).xpath('.//div[@class="col-md-6  text-default small-screen-default"]//text()'))
        output.append(base_url) # url
        output.append(details[0]) #location name
        output.append(details[1]) #address
        address = details[2].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(details[3].replace('Tel', '')) #phone
        output.append("Tio's Mexican Food") #location type
        geo_loc = store.split('"latlng":[')[1].split(']')[0].replace('"', '').split(',')
        output.append(geo_loc[0]) #latitude
        output.append(geo_loc[1]) #longitude
        output.append(validate(details[5:-1])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
