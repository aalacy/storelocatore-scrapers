import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://originalmels.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\xa0', ' ').encode('ascii', 'ignore').encode("utf8").strip().replace('\n', '')

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
    url = "https://originalmels.com/locations/"
    session = requests.Session()
    request = session.get(url)    
    source = validate(request.text.split('var wpgmaps_localize_marker_data = ')[1].split('var wpgmaps_localize_global_settings')[0])[:-1]
    store_list = etree.HTML(request.text).xpath('//div[contains(@class, "fusion-fullwidth fullwidth-box hundred-percent-fullwidth")]//div[@class="fusion-column-wrapper"]')
    map_list = json.loads(source)
    map_data = {}
    for key, map in map_list.items():
        map_data[map['title'].lower().replace('-', '').replace(' ', '')] = {
            'latitude' : map['lat'],
            'longitude' : map['lng']
        }        
    for idx, store in enumerate(store_list):
        store = store.xpath('.//div[@class="fusion-text"]')
        if store != []:
            output = []
            output.append(base_url) # url
            output.append(get_value(store[0].xpath('.//text()'))) #location name
            detail = eliminate_space(store[1].xpath('.//text()'))
            address = parse_address(', '.join(detail[:-2]).replace('T:', ''))
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode   
            output.append('US') #country code
            output.append('<MISSING>') #store_number
            output.append(detail[-2].replace('T:', '').strip()) #phone
            output.append("The Original Mels Diners") #location type
            key = output[1].lower().replace('-', '').replace(' ', '').replace('nevada', 'nv')
            if  key in map_data:
                output.append(map_data[key]['latitude']) #latitude
                output.append(map_data[key]['longitude']) #longitude
            else:
                output.append('<MISSING>') #latitude
                output.append('<MISSING>') #longitude
            store_hours = eliminate_space(store[2].xpath('.//text()'))
            output.append(get_value(', '.join(store_hours[:-1])).replace('Hours', '')[1:]) #opening hours        
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
