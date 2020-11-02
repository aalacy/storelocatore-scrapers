import csv
import re
from lxml import etree
import json
import usaddress
from sgrequests import SgRequests

base_url = 'https://wokcanorestaurant.com'

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
    url = "https://wokcanorestaurant.com/locations/"
    session = SgRequests()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="et_pb_text_inner"]')
    for store in store_list:
        content = ' '.join([x for x in store.itertext()])
        if 'tel:' not in content.lower():
            continue
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath('.//h2//text()'))) #location name        
        address = parse_address(validate(store.xpath('.//p//a//text()')))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode 
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        details = eliminate_space(store.xpath('./p/text()'))
        output.append(details[0].replace('Tel:', '').replace('Phone:', '')) #phone
        output.append("Wokcano Restaurants") #location type
        geo_loc = validate(store.xpath('.//p//a/@href')).split('/@')[1].split(',17z')[0].split(',')
        output.append(geo_loc[0]) #latitude
        output.append(geo_loc[1]) #longitude
        output.append(get_value(details[2:]).replace('Hrs:', '').strip()) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
