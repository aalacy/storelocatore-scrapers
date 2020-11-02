import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.thelashlounge.com'

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
    url = "https://www.thelashlounge.com/salons/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('.//a[@class="location-bottom-link"]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath('.//h2//text()'))) #location name
        output.append(get_value(store.xpath('.//span[@itemprop="streetAddress"]//text()'))) #address
        output.append(get_value(store.xpath('.//span[@itemprop="addressLocality"]//text()'))) #city
        output.append(get_value(store.xpath('.//span[@itemprop="addressRegion"]//text()'))) #state
        output.append(get_value(store.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
        output.append("The Lash Lounge Salons") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        store = etree.HTML(session.get(validate(store.xpath('./@href'))).text)
        store_hours = get_value(', '.join(eliminate_space(store.xpath('.//div[@class="home-contact-content"]//li//text()'))))        
        if store_hours == '<MISSING>':
            temp = store.xpath('.//div[@class="pre-footer-details"]')
            if len(temp) > 0:
                store_hours = get_value(' '.join(eliminate_space(temp[0].xpath('.//ul//li//text()'))))
        output.append(store_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
