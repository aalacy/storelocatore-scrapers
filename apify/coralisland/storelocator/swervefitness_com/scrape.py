import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.swervefitness.com'

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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = "https://www.swervefitness.com"
    output_list = []
    page_url = ''
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//ul[@class="dropdown-menu"]')[0].xpath('.//a/@href')
    for store_link in store_list:
        store_link = base_url + store_link
        store = etree.HTML(session.get(store_link).text)
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(validate(store.xpath('.//div[@class="page-header classes"]//h1//text()'))) #location name
        address = validate(store.xpath('.//h3//text()')).replace('/', ',')
        phone = validate(store.xpath('.//h4//text()'))
        if address == '':
            address = eliminate_space(store.xpath('.//h4//text()'))[0].replace('/', ',')
            phone = validate(eliminate_space(store.xpath('.//h4//text()'))[1])
        address = parse_address(address)
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(phone) #phone
        output.append("SWERVE Fitness") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        store_hours = []
        # hours = store.xpath('.//table[@class="scheduleTable"]//tbody//tr//td')
        # days_of_week = eliminate_space(store.xpath('.//table[@class="scheduleTable"]//span[@class="thead-dow"]//text()'))
        # for idx, day in enumerate(days_of_week):
        #     hour = day + ' ' + validate(eliminate_space(hours[idx].xpath('.//text()')))
        #     store_hours.append(hour)
        output.append(get_value(', '.join(store_hours))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
