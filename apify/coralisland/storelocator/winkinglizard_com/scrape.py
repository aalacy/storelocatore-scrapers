import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://winkinglizard.com'

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
    url = "https://winkinglizard.com/locations"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('.//div[@class="medium-12 columns"]//a[@class="button"]/@href')
    for link in store_list:
        link = base_url + link
        store = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h1//text()'))) #location name
        detail = eliminate_space(store.xpath('.//div[@class="medium-6 columns"]')[0].xpath('.//text()'))
        output.append(detail[1]) #address
        address = detail[2].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        h_temp = ''
        phone = ''
        for idx, hour in enumerate(detail[5:]):
            if 'phone' in hour.lower():
                phone = detail[idx+6]
                break
            h_temp += hour + ' '
        output.append(get_value(phone)) #phone
        output.append("Winking Lizard Restaurant and Tavern | Winking Lizard") #location type
        geolocation = validate(store.xpath('.//div[@class="medium-6 columns"]//a/@href')).split('@')[1].split(',')
        output.append(geolocation[0]) #latitude
        output.append(geolocation[1]) #longitude
        output.append(h_temp) #opening hours            
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
