import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.westsidepizza.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "https://www.westsidepizza.com/locations/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="locations-list"]//div[@class="views-row"]')
    for link in store_list:
        link = base_url + link.xpath('.//span[@class="field-content"]//a/@href')[0]
        store = etree.HTML(session.get(link).text)
        output = []        
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h1//text()'))) #location name
        output.append(get_value(store.xpath('.//div[@class="field-address"]//text()'))) #address
        output.append(get_value(store.xpath('.//div[@class="field-city"]//text()'))) #city
        output.append(get_value(store.xpath('.//div[@class="field-state"]//text()'))) #state
        output.append(get_value(store.xpath('.//div[@class="field-zip-code"]//text()'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//div[@class="field-phone"]//text()'))) #phone
        output.append("Westside Pizza") #location type
        output.append(get_value(store.xpath('.//meta[@property="latitude"]//@content'))) #latitude
        output.append(get_value(store.xpath('.//meta[@property="longitude"]//@content'))) #longitude
        output.append(get_value(', '.join(eliminate_space(store.xpath('.//div[@class="fieldset-wrapper"]/div[@class="body"]//text()'))))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
