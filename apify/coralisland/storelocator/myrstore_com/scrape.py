import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://www.myrstore.com'

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
    url = "http://www.myrstore.com/locations"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="col-md-4 margin bottom-lg"]')
    mapList = source.split('var companyPos')[1:]    
    for idx, store in enumerate(store_list):
        output = []
        output.append(base_url) # url
        loc_name = validate(store.xpath('.//a//text()')).split('-')
        output.append(loc_name[1]) #location name
        address = eliminate_space(store.xpath('./text()'))
        phone = ''
        if len(address) > 2:
            phone = address[2]
        address = parse_address(', '.join(address[:2]))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append(loc_name[0].replace('#', '')) #store_number
        output.append(get_value(phone)) #phone
        output.append("R Store") #location type
        link = base_url + validate(store.xpath('.//a/@href'))
        store_hours = eliminate_space(etree.HTML(session.get(link).text).xpath('.//table//text()'))        
        geo_loc = validate(mapList[idx].split('maps.LatLng(')[1].split(');')[0]).split(',')
        if len(geo_loc) > 1:
            output.append(geo_loc[0]) #latitude
            output.append(geo_loc[1]) #longitude
        else:
            output.append('<MISSING>') #latitude
            output.append('<MISSING>') #longitude
        output.append(get_value(store_hours)) #opening hours          
        if len(store_hours) != 7:
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
