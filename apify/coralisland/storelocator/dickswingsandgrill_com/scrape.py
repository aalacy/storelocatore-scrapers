import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://dickswingsandgrill.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\n', '').strip()

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
    url = "https://dickswingsandgrill.com/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[contains(@class, "vc_parallax vc_parallax-none")]//a')[1:]
    for link in store_list:
        name = get_value(link.xpath('.//text()'))
        link = get_value(link.xpath('./@href'))
        if 'http' not in link:
            link = base_url + link
        store = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        output.append(name) #location name
        detail = validate(store.xpath('.//div[@class="wpb_text_column wpb_content_element "]//h2//text()')).split('(')
        if detail[0] == '':
            output.append('<MISSING>') #address
        else:
            output.append(detail[0]) #address        
        output.append('<MISSING>') #city
        output.append('<MISSING>') #state
        output.append('<MISSING>') #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        if detail[0] == '':
            output.append('<MISSING>') #phone
        else:
            output.append('('+detail[1].replace('Weekly Specials', '')) #phone
        output.append("Dicks Wings and Grill") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        store_hours = store.xpath('.//div[@class="wpb_text_column wpb_content_element "]')
        if len(store_hours) == 3:
            store_hours = get_value(store_hours[1].xpath('.//text()'))
        else:
            store_hours = '<MISSING>'
        output.append(store_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
