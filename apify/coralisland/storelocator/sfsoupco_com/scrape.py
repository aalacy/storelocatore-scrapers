import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'http://www.sfsoupco.com'

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
    url = "http://www.sfsoupco.com/index.php?id=17"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="location-area-green"]//a[@class="location"]/@href')
    for link in store_list:
        link = base_url + '/' + link
        store = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        output.append(eliminate_space(store.xpath('.//h1//text()'))[0]) #location name
        detail = eliminate_space(store.xpath('//table[@width="411"]//text()'))
        address = ''
        phone = ''
        store_hours = ''
        for idx, de in enumerate(detail):
            if 'telephone' in de.lower():
                address = get_value(detail[0] + ', ' +detail[idx-1])
                phone = get_value(detail[idx+1])
            if 'hours' in de.lower():
                store_hours = get_value(detail[idx+1:])
        address = parse_address(address)
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode   
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(phone) #phone
        output.append("San Francisco Soup Company - Restaurant Locations") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(store_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
