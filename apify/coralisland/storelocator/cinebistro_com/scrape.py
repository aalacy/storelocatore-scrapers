import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://cinebistro.com'

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
        if item != '' and 'directions' not in item.lower():
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
    url = "https://cinebistro.com/locations.php"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="locationbox"]')
    for store in store_list[:-1]:        
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//div[@class="fn org"]//a//text()')).replace('  ', '')) #location name
        address = eliminate_space(store.xpath('.//div[@class="street-address"]//text()'))
        phone = ''
        if len(address) > 2:
            address = validate(address)
            phone = get_value(re.findall("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}", address))
            address = parse_address(address.replace(phone, ''))
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode
        else:
            output.append(get_value(store.xpath('.//div[@class="street-address"]//text()'))) #address    
            output.append(get_value(store.xpath('.//span[@class="locality"]//text()'))) #city
            output.append(get_value(store.xpath('.//span[@class="region"]//text()'))) #state
            output.append(get_value(store.xpath('.//span[@class="postal-code"]//text()'))) #zipcode
            phone = get_value(store.xpath('.//span[@class="phone"]//text()'))
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(phone) #phone
        output.append("The Ultimate Dinner and a Movie Experience | CMX CineBistro") #location type
        output.append('<MISSING>') #latitude
        output.append('<MISSING>') #longitude
        output.append('<MISSING>') #opening hours
        if output[5] != '<MISSING>':
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
