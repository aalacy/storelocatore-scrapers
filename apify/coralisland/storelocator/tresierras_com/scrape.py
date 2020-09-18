import csv
import re
import pdb
from lxml import etree
import json
import usaddress
from sgrequests import SgRequests

base_url = 'http://tresierras.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

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
            zipcode = addr[0]
        elif addr[1] == 'StateName':
            state = addr[0]
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
    session = SgRequests()
    output_list = []
    url = "http://tresierras.com/locations.aspx"
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@id="subRightCol2"]//div[@class="addressShowText"]')
    for store in store_list:
        geolocation = validate(store.xpath('.//small//a/@href')).split('&sll=')[1].split('&sspn')[0].split(',')
        store = eliminate_space(store.xpath('.//div[@class="boldGreen"]//text()'))
        output = []
        output.append(base_url) # url
        output.append(store[0]) #location name
        address = parse_address(store[1])
        output.append(address['street']) #address        
        output.append(address['city']) #city
        output.append(address['state'].replace('.', '')) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[2].split('fax')[0].replace('phone: ', '')) #phone
        output.append("Tresierras Supermarkets") #location type        
        output.append(geolocation[0]) #latitude
        output.append(geolocation[1]) #longitude
        output.append(validate(store[3].split(':')[1])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
