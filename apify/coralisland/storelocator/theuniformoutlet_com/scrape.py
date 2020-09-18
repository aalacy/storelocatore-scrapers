import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://theuniformoutlet.com'

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
            zipcode = addr[0]
        elif addr[1] == 'StateName':
            state = addr[0]
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
    url = "https://theuniformoutlet.com/find-a-store/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[contains(@class, "location-result")]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        link = get_value(store.xpath('.//h2//a/@href'))
        output.append(get_value(store.xpath('.//h2//text()'))) #location name
        address = parse_address(get_value(store.xpath('.//address[@class="address"]//text()')))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state'].replace(',', '')) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//address[@class="phone"]//text()'))) #phone
        output.append("The Uniform Outlet") #location type
        output.append(get_value(store.xpath('./@data-lat'))) #latitude
        output.append(get_value(store.xpath('./@data-lng'))) #longitude
        detail = etree.HTML(session.get(link).text)
        store_hours = eliminate_space(detail.xpath('.//div[@class="content-left"]//text()'))        
        start_point = 0
        end_point = 0
        for idx, hour in enumerate(store_hours):
            if 'hours:' in hour.lower() or 'shop with us' in hour.lower():
                start_point = idx + 1
            if 'pm' in hour.lower() and ':' in hour.lower():
                end_point = idx + 1
        output.append(get_value(', '.join(store_hours[start_point:end_point]))) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
