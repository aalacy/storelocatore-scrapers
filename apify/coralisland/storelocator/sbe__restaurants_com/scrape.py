import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.sbe.com/restaurants/brands/cleo/'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\\u2013', '').strip().replace('\n', '')

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
    url = "https://www.sbe.com/restaurants/brands/cleo/"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//a[@class="ftr-itm-hrf item-click"]/@href')
    for store_link in store_list:
        store = etree.HTML(session.get(store_link).text)        
        output = []
        output.append(base_url) # url
        loc_name = eliminate_space(store_link.split('/'))[-1].replace('-', ' ').upper()
        output.append(loc_name) #location name
        street = validate(store.xpath('.//div[@class="address_hours center"]//span[contains(@class, "address1")]//text()'))
        if ':' in street:
            street = street.split(':')[1]
        output.append(street) #address
        output.append(eliminate_space(store.xpath('.//div[@class="address_hours center"]//span[contains(@class, "city")]//text()'))[0].replace(',', '')) #city
        output.append(validate(store.xpath('.//div[@class="address_hours center"]//span[contains(@class, "state")]//text()'))) #state
        zipcode = validate(store.xpath('.//div[@class="address_hours center"]//span[contains(@class, "postal_code")]//text()'))
        if zipcode != '':
            output.append(zipcode) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(validate(store.xpath('.//div[@class="large"]//a/text()')[0])) #phone            
            output.append("Ciel Spa at Delano South Beach | Restaurants") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            store_hours = validate(store.xpath('.//div[@class="text-spaced-extra more_info"]//text()')).replace('Hours of Operation:', '')
            output.append(store_hours) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
