import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.applegreenstores.com'

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
    url = "https://www.applegreenstores.com/us/locations/"
    page_url = ''
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': 'cookielawinfo-checkbox-Necessary=yes; cookielawinfo-checkbox-Non-necessary=yes; cookielawinfo-checkbox-non-necessary=yes',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }
    source = session.get(url,  headers=headers).text
    response = etree.HTML(source)
    state_list = response.xpath('//div[@class="ag-tile open-tile"]//a/@href')
    for state_link in state_list:
        state = etree.HTML(session.get(state_link, headers=headers).text)
        store_list = state.xpath('.//div[@class="ag-tile"]//tr')[1:]
        for store in store_list:
            address = eliminate_space(store.xpath('.//text()'))[0]
            output = []
            output.append(base_url) # url
            output.append(state_link) # page url
            output.append('<MISSING>') #location name          
            address = parse_address(address)
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append('<MISSING>') #phone
            output.append("Low Fuel Prices Always | Applegreen US") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            output.append("<MISSING>") #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
