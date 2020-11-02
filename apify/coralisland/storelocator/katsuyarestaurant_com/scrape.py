import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://www.katsuyarestaurant.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.strip().replace('\r', '').replace('\n', '')

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
    url = "https://www.katsuyarestaurant.com"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//ul[@class="locations-gallery"]//a/@href')
    for store_link in store_list:
        store_link = base_url + store_link
        store = etree.HTML(session.get(store_link).text)
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath('.//div[@class="locations-holder"]//div[@class="location_name"]//text()'))) #location name
        address = validate(store.xpath('.//div[@class="locations-holder"]//div[@class="address"]//text()'))
        address = parse_address(address)
        if address['zipcode'] != "<MISSING>":
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(validate(store.xpath('.//div[@class="locations-holder"]//div[@class="telephone"]//text()')[0])) #phone
            output.append("Katsuya Restaurant") #location type
            output.append("<INACCESSIBLE>") #latitude
            output.append("<INACCESSIBLE>") #longitude
            store_hours = validate(store.xpath('.//div[@class="schedule-box"]//meta[@itemprop="openingHours"]/@content'))
            output.append(get_value(store_hours)) #opening hours            
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
