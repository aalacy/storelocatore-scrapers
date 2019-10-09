import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://www.thecamptc.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "https://www.thecamptc.com/locations.php"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="col-md-3 col-sm-6"]//a')
    for store_link in store_list[:-2]:
        city_state = eliminate_space(validate(store_link.xpath('.//text()')).split(', '))
        store_link = base_url + '/' + validate(store_link.xpath('./@href'))
        store = etree.HTML(session.get(store_link).text)
        details = eliminate_space(store.xpath('.//div[@class="container content"]//text()'))
        output = []
        phone = get_value(re.findall("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}", ', '.join(details))[0])
        output.append(base_url) # url
        output.append(', '.join(city_state)) #location name
        address = details[1]
        if '@' not in details[2] and '-' not in details[2]:
            address += ', ' + details[2]
        address = parse_address(address)
        output.append(address['street'].replace(phone, '')) #address
        if address['city'] == '<MISSING>':
            output.append(city_state[0])
            output.append(city_state[1])
        else:
            output.append(address['city']) #city
            output.append(address['state']) #state            
        output.append(address['zipcode']) #zipcode 
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(phone) #phone
        output.append("TheCampTC") #location type
        geo_loc = validate(store.xpath('.//div[@class="container content"]//iframe/@src')).split('!2d')[1].split('!2m')[0].split('!3d')
        output.append(geo_loc[0]) #latitude
        output.append(geo_loc[1]) #longitude
        output.append(validate(details[5:])) #opening hours            
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
