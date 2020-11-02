import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://myclarkspns.com'

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
    url = "https://myclarkspns.com"
    session = requests.Session()
    source = session.get(url).text
    store_list = eliminate_space(source.split('window.properties = [')[1].split('];')[0].split('],'))
    for store in store_list:
        store = store[1:].split("',")
        output = []
        output.append(base_url) # url
        output.append(store[0].replace("'", "").replace('&#8217;', "'")) #location name
        details = eliminate_space(etree.HTML(store[1]).xpath('.//text()'))
        phone = ''
        address = []
        for de in details:
            if '-'  in de:
                phone = de
            else:
                address.append(de)
        address = parse_address(validate(address))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(phone)) #phone
        output.append("Clark's Pump-N-Shop | Return, Refresh, Refuel!") #location type
        geo_loc = store[2].split(',')
        output.append(geo_loc[0]) #latitude
        output.append(geo_loc[1]) #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
