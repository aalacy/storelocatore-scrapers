import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://www.fordsgarageusa.com'

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.fordsgarageusa.com/locations/"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="service-item-inner"]')
    for store in store_list:
        store_link = base_url + validate(store.xpath('.//h4//a/@href'))
        store = eliminate_space(store.xpath('.//text()'))        
        address = ''
        phone = ''
        store_hours = ''
        sh_start = 0
        for idx, st in enumerate(store):
            if 'phone' in st.lower():
                phone = store[idx+1]
                address = validate(store[2:idx])
            if 'hours' in st.lower():
                sh_start = idx + 1                
            if 'view' in st.lower():
                store_hours = store[sh_start:idx]
        output = []
        output.append(base_url) # url
        output.append(store[0]) #location name
        address = parse_address(address)
        output.append(address['street']) #address
        details = etree.HTML(session.get(store_link).text)
        if address['city'] =='<MISSING>':
            address_ = validate(eliminate_space(details.xpath('.//p[@class="hours-row"]//text()'))[-2:])
            address = parse_address(address_)
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode   
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(phone)) #phone
        output.append("Fords Garage") #location type
        geo_loc = eliminate_space(validate(details.xpath('.//div[@class="mtheme-cell-inner"]//iframe/@src')).split('!2d'))
        if len(geo_loc) > 0:
            geo_loc = geo_loc[1].split('!2m')[0].split('!3d')
            output.append(geo_loc[0]) #latitude
            output.append(geo_loc[1]) #longitude
        else:
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
