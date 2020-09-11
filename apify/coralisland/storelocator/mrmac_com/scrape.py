import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.mrmac.com'

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
    url = "https://www.mrmac.com/locations-salt-lake-city-utah/#locations"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="wpgmza-basic-listing-content-holder"]')
    for store in store_list:        
        geo_loc = validate(store.xpath('.//a[@class="wpgmza_gd"]/@gps')).split(',')
        store = eliminate_space(store.xpath('.//text()'))
        phone = ''
        store_hours = ''
        for idx, st in enumerate(store):
            if 'phone' in st.lower():
                phone = validate(store[idx+1])
            if 'hours' in st.lower():
                store_hours = store[idx+1:-2]
        output = []
        output.append(base_url) # url
        output.append(store[0]) #location name
        address = store[1].split(',')
        output.append(address[0]) #address        
        output.append(address[1]) #city
        output.append(address[2]) #state
        output.append('<MISSING>') #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(phone)) #phone
        output.append("Mr Mac | Men's Suits & Missionary Clothing for Elders") #location type
        output.append(get_value(geo_loc[0])) #latitude
        output.append(get_value(geo_loc[1])) #longitude
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
