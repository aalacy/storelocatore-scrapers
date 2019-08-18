import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.ifratellipizza.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").replace('\n', '').replace('\t', '').strip()

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
    url = "https://www.ifratellipizza.com/locations/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@id="locations-listings"]//a/@href')
    for store in store_list:        
        store = etree.HTML(session.get(store).text)
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//span[@class="heading"]//text()'))) #location name
        output.append(get_value(store.xpath('.//span[@itemprop="streetAddress"]//text()'))) #address
        output.append(get_value(store.xpath('.//span[@itemprop="addressLocality"]//text()'))) #city
        output.append(get_value(store.xpath('.//span[@itemprop="addressRegion"]//text()'))) #state
        output.append(get_value(store.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
        output.append("i Fratelli Pizza") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(get_value(', '.join(eliminate_space(store.xpath('.//meta[@itemprop="openingHours"]//@content'))))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
