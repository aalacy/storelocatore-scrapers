import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.aman.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "https://www.aman.com/"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@id="block-menu-block-1"]//a')
    for link in store_list:
        txt = validate(link.xpath('.//text()')).lower()
        if ', usa' in txt and 'soon' not in txt:
            url = base_url + validate(link.xpath('./@href'))
            store = etree.HTML(session.get(url).text)
            output = []
            output.append(base_url) # url
            detail = eliminate_space(store.xpath('.//div[@class="medium-14 large-6 columns"]//text()'))
            output.append(detail[0]) #location name
            if len(detail) == 2:
                address = detail[1].replace('.', '').split(',')
                output.append(address[0]) #address
                address = address[1].split(' ')
                output.append(validate(address[:-2])) #city
                output.append(address[-2]) #state
                output.append(address[-1]) #zipcode
            else:
                output.append(detail[1]) #address
                output.append(detail[2]) #city
                address = detail[3].replace(',', '').split(' ')
                output.append(address[0]) #state
                output.append(address[1]) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            phone_temp = eliminate_space(store.xpath('.//div[@class="medium-14 large-8 columns data-phones"]//a/@href'))
            phone = ''
            for ph in phone_temp:
                if 'tel' in ph:
                    phone = ph.split(':')[1]
            output.append(get_value(phone)) #phone
            output.append("Aman Resorts, Hotels & Residences - Explore Luxury Destinations") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            output.append("<MISSING>") #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
