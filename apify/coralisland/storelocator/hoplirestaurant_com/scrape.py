import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://hoplirestaurant.com'

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
    url = "http://hoplirestaurant.com"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Proxy-Authorization': 'Basic NDZpemNMeFdzbXo2VXdmQWNlcDFxeXhSOlE3a0RlcHM4MjlBd3lmSG9KTjFXZ0Z0Vg==',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    session = requests.Session()
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)    
    store_list = response.xpath('.//a/@href')
    for link in store_list:
        link = base_url + '/' + link
        data = etree.HTML(session.get(link, headers=headers).text)
        store = eliminate_space(data.xpath('.//p[@class="style3"]//text()'))
        if len(store) > 0:
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
            h_temp = ''
            phone = ''
            for idx, hour in enumerate(store[3:]):
                if 'tel' in hour.lower():
                    phone += get_value(hour.lower().replace('tel', '')) + ' '
                if 'operation' in hour.lower():
                    h_temp = ', '.join(store[idx+4:])
            output.append(get_value(phone)) #phone
            output.append("Hop Li Seafood Restaurant- Westside") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            output.append(h_temp) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
