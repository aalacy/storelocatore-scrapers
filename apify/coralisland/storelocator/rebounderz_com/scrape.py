import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://www.rebounderz.com'

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
    url = "https://www.rebounderz.com/all-locations/"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': '__cfduid=d354d5b0e610f9ab1fb44b0ade0e85eba1564784754; PHPSESSID=608df9ae032ca987733f2631ee4f27d9',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class=" grid-unit size1of3"]')
    for store in store_list:
        store = eliminate_space(store.xpath('.//text()'))
        output = []
        address_point = 0
        phone_point = 0
        for idx, st in enumerate(store):
            if 'Address:' == st:
                address_point = idx
            if 'Phone:' == st:
                phone_point = idx
        if phone_point != 0:
            phone = store[phone_point+1]
        address = parse_address(validate(store[address_point+1:phone_point]))
        output.append(base_url) # url
        output.append(store[0]) #location name
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode   
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(phone) #phone
        output.append("Indoor Trampoline Arena and Family Fun Center - Rebounderz") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append("<MISSING>") #opening hours
        if 'panama' not in address['street'].lower():
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
