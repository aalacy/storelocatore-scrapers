import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.unitedway.org'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

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

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '') + ' '
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.unitedway.org/local/united-states"
    session = requests.Session()            
    state_list = etree.HTML(session.get(url).text).xpath('.//a[@class="image-touts__tout"]/@href')
    for state_link in state_list:
        if 'http' not in state_link:
            state_link = base_url + '/' + state_link
            store_list = etree.HTML(session.get(state_link).text).xpath('.//ul[@class="usa-state__list"]//a/@href')
            for store_link in store_list:
                if 'http' not in store_link:
                    store_link = base_url + store_link
                store = etree.HTML(session.get(store_link).text)
                output = []
                output.append(base_url) # url
                output.append(store_link) # page url
                output.append(validate(store.xpath('.//p[@class="usa-local__contact-details"]//span[@itemprop="name"]//text()'))) #location name
                output.append(validate(store.xpath('.//p[@class="usa-local__contact-details"]//span[@itemprop="streetAddress"]//text()'))) #address
                citystate = validate(store.xpath('.//p[@class="usa-local__contact-details"]//span[@itemprop="addressLocality"]//text()')).split(',')
                output.append(citystate[0]) #city
                output.append(citystate[1]) #state
                output.append(validate(store.xpath('.//p[@class="usa-local__contact-details"]//span[@itemprop="postalCode"]//text()'))) #zipcode  
                output.append('US') #country code
                output.append("<MISSING>") #store_number
                output.append(get_value(store.xpath('.//p[@class="usa-local__contact-details"]//span[@itemprop="telephone"]//text()'))) #phone
                output.append("United Way Worldwide") #location type
                output.append("<MISSING>") #latitude
                output.append("<MISSING>") #longitude
                output.append("<MISSING>") #opening hours
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
