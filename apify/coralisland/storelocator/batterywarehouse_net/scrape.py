import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://www.batterywarehouse.net'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\r', '').replace('\n', '').strip()

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
    url = "https://www.batterywarehouse.net/battery_warehouse_locations_batteries_Maryland_Delaware_Pennsylvania.php"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    cl_store_list = response.xpath('//div[@class="col-lg-6 col-md-6 col-sm-6"]')[1].xpath('.//a/@href')
    for link in cl_store_list:        
        if 'http' not in link:
            link = base_url + '/' + link
        store = etree.HTML(session.get(link).text)
        detail = eliminate_space(store.xpath('.//div[@id="headerInfo"]//text()')) 
        output = []
        output.append(base_url) # url
        output.append(detail[1]) #location name
        address = parse_address(detail[2] + ', ' + detail[3])
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(detail[0]) #phone
        output.append("Battery Warehouse") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(get_value(eliminate_space(store.xpath('.//div[@class="col-lg-10 col-md-10 col-sm-10"]//h3//text()'))).replace('Hours:', '').replace('  ', '')) #opening hours        
        output_list.append(output)
    al_store_list = response.xpath('//div[@class="col-lg-6 col-md-6 col-sm-6"]')[2].xpath('.//a/@href')
    for link in al_store_list:        
        if 'http' not in link:
            link = base_url + '/' + link
        store = etree.HTML(session.get(link).text)
        detail = eliminate_space(store.xpath('.//div[@class="col-lg-12 col-md-12 col-sm-12"]')[0].xpath('.//text()')) 
        output = []            
        output.append(base_url) # url
        output.append(detail[0]) #location name
        address = parse_address(detail[2].replace('Address:', ''))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(detail[1].replace('Phone:', '')) #phone
        output.append("Battery Warehouse") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append('<MISSING>') #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
