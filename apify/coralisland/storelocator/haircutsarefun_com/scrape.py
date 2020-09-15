import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.haircutsarefun.com'

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
        if item != '' and 'open' not in item.lower():
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
    url = "https://www.haircutsarefun.com/store-locator/"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    tables = response.xpath('//table[@style="text-align:left;margin-left:50px;"]')
    for t_idx, table in enumerate(tables):
        store_list = table.xpath('.//a[contains(@style, "font-size:14px;")]/@href')
        for store_link in store_list:
            store = etree.HTML(session.get(store_link).text)
            if t_idx == 0:
                details = eliminate_space(store.xpath('.//span[@style="color:#0D349B;font-size:16px;"]//text()'))
                address = ''
                phone = ''
                store_hours = ''
                for idx, de in enumerate(details):
                    if 'phone' in de.lower():
                        address = validate(details[:idx])
                        phone = details[idx+1]
                    if 'hours' in de.lower():
                        store_hours = validate(details[idx+1:])
                output = []
                output.append(base_url) # url
                output.append(validate(store.xpath('.//span[@style="color:#0D349B;font-size:28px;text-align:left;"]//text()'))) #location name
                address = parse_address(address)
                if address['zipcode'] != '<MISSING>':
                    output.append(address['street']) #address
                    output.append(address['city']) #city
                    output.append(address['state']) #state
                    output.append(address['zipcode']) #zipcode   
                    output.append('US') #country code
                    output.append("<MISSING>") #store_number
                    output.append(get_value(phone)) #phone
                    output.append("Cookie Cutters - Haircuts for Kids") #location type
                    output.append("<MISSING>") #latitude
                    output.append("<MISSING>") #longitude
                    if 'coming' not in get_value(store_hours).lower():
                        output.append(get_value(store_hours)) #opening hours
                        output_list.append(output)
                else:
                    if len(address['state']) > 4 and 'missing' not in address['state'].lower():
                        output.append(address['street']) #address
                        output.append(address['city']) #city
                        output.append(address['state'][:2]) #state
                        output.append(address['state'][2:]) #zipcode   
                        output.append('US') #country code
                        output.append("<MISSING>") #store_number
                        output.append(get_value(phone)) #phone
                        output.append("Cookie Cutters - Haircuts for Kids") #location type
                        output.append("<MISSING>") #latitude
                        output.append("<MISSING>") #longitude
                        if 'coming' not in get_value(store_hours).lower():
                            output.append(get_value(store_hours)) #opening hours
                            output_list.append(output)
            else:
                details = eliminate_space(store.xpath('.//span[@style="color:#0D349B;font-size:16px;"]//text()'))
                address = ''
                phone = ''
                store_hours = ''
                for idx, de in enumerate(details):
                    if 'phone' in de.lower():
                        address = details[:idx]
                        phone = details[idx+1]
                    if 'hours' in de.lower():
                        store_hours = validate(details[idx+1:])
                output = []
                output.append(base_url) # url
                output.append(validate(store.xpath('.//span[@style="color:#0D349B;font-size:28px;text-align:left;"]//text()'))) #location name
                output.append(address[0]) #address
                csz = eliminate_space(address[1].replace(',', '').split(' '))
                output.append(validate(csz[:-3])) #city
                output.append(csz[-3]) #state
                output.append(validate(csz[-2:])) #zipcode   
                output.append('CA') #country code
                output.append("<MISSING>") #store_number
                output.append(get_value(phone)) #phone
                output.append("Cookie Cutters - Haircuts for Kids") #location type
                output.append("<MISSING>") #latitude
                output.append("<MISSING>") #longitude
                output.append(get_value(store_hours)) #opening hours
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
