import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://texascartitleandpaydayloanservicesinc.com'


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
    url = "https://texascartitleandpaydayloanservicesinc.com/closest-stores?loan_type=all&num=0"
    page_url = ''
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)['locations']
    for store in store_list:
        store_link = base_url + '/' + validate(store['store_url'])
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(get_value(store['business_name'])) #location name
        output.append(get_value(store['address_line_1'])) #address
        output.append(get_value(store['locality'])) #city
        output.append(get_value(store['administrative_area'])) #state
        output.append(get_value(store['postal_code'])) #zipcode
        output.append(get_value(store['country'])) #country code
        output.append(get_value(store['id'])) #store_number
        output.append(get_value(store['primary_phone'])) #phone
        output.append('HappyFox Chat Widget IFrame') #location type
        output.append(get_value(store['latitude'])) #latitude
        output.append(get_value(store['longitude'])) #longitude
        store_hours = []
        hours = etree.HTML(session.get(store_link).text).xpath('.//div[@class="twofive"]/p')
        if len(hours) > 0:            
            store_hours = eliminate_space(hours[0].xpath('.//text()'))
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
