import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://sterlingoptical.com'

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
            state = addr[0].replace(',', '')
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
    url = "https://sterlingoptical.com/locations/"
    page_url = ''
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="col-md-4 single-location"]')
    for store in store_list:
        store_link = validate(store.xpath('.//a[@class="link-emphasis single-location-link"]/@href'))
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(validate(store.xpath('.//h4[@class="single-location-title"]//text()'))) #location name
        details = eliminate_space(store.xpath('.//p//text()'))
        address = ''
        phone = ''
        for idx, de in enumerate(details):
            if 'phone' in de.lower():
                address = ', '.join(details[:idx])
                phone = details[idx+1]
        address = parse_address(address)
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(phone)) #phone
        output.append("Sterling Optical") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        more_info = etree.HTML(session.get(store_link).text)
        store_hours = eliminate_space(more_info.xpath('.//ul[@class="location-hours-list store-hours"]//text()'))
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
