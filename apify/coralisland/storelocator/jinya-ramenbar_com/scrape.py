import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'http://jinya-ramenbar.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
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
    url = "http://jinya-ramenbar.com/locations"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//dd[@class="shop-list"]')
    for store in store_list:        
        output = []
        store_link = base_url + validate(store.xpath('.//a/@href'))
        output.append(base_url) # url            
        title = validate(store.xpath('.//div[@class="shop-name"]//text()'))
        if 'soon' not in title.lower():
            output.append(title) #location name
            address = validate(store.xpath('.//div[@class="shop-address"]//text()'))
            if 'canada' not in address.lower():
                address = parse_address(address)
                output.append(address['street']) #address
                output.append(address['city']) #city
                output.append(address['state']) #state
                output.append(address['zipcode']) #zipcode  
                output.append('US') #country code
            else:
                address = eliminate_space(address.replace('Canada', '').split(','))
                city = address[-2].split(' ')
                if len(city) < 2:
                    output.append(get_value(address[:-2])) #address
                    output.append(get_value(address[-2])) #city
                else:
                    output.append(get_value(address[:-1]).replace(city[-1], '')) #address
                    output.append(city[-1]) #city
                output.append(get_value(address[-1][:-7])) #state
                output.append(get_value(address[-1][-7:])) #zipcode  
                output.append('CA') #country code
            output.append("<MISSING>") #store_number
            details = etree.HTML(session.get(store_link).text)
            store_hours = eliminate_space(details.xpath('.//div[@class="shop-text"]//ul//li')[0].xpath('.//text()'))
            phone = eliminate_space(details.xpath('.//h3//text()'))
            output.append(get_value(phone[0])) #phone
            output.append("jinya-ramenbar") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            if len(phone) > 1:
                output.append(phone[1] + ' ' + get_value(store_hours)) #opening hours
            else:
                output.append(get_value(store_hours)) #opening hours
            output_list.append(output)                
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
