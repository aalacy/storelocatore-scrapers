import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.barreforte.com/locations/colorado-springs-colorado/'

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
    output_list = []
    url = "https://www.barreforte.com/locations"
    page_url = ''
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="tm_pb_toggle_content clearfix"]//a/@href')
    for store_link in store_list:
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        store = etree.HTML(session.get(store_link).text)        
        location_name = validate(store.xpath('.//div[contains(@class, "tm_pb_text_0")]//h3//text()')).replace('NOW OPEN!', '')
        if location_name == '':
            location_name = validate(store.xpath('.//div[contains(@class, "tm_pb_text_0")]//h2//text()')).replace('NOW OPEN!', '')
        output.append(location_name) #location name
        details = validate(eliminate_space(store.xpath('.//div[contains(@class, "tm_pb_text_0")]//h4/text()')))
        phone = validate(re.findall(r'[(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', details))
        phone_split = eliminate_space(phone.split('('))
        if len(phone_split) > 1:
            phone = phone_split[1]
            address = validate(details.replace(phone, '').replace('|', ',')) + phone_split[0]
        else:
            address = validate(details.replace(phone, '').replace('|', ','))
        address = parse_address(address)
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append("<MISSING>") #store_number        
        output.append(get_value(phone)) #phone
        output.append("Barre Studios and Fitness Classes | Barre Forte") #location type
        geo_loc = validate(store.xpath('.//div[@class="mapDir"]//a/@href')).split('@')
        if len(geo_loc) > 1:
            geo_loc = eliminate_space(geo_loc[1].split('17z')[0].split(','))
            output.append(get_value(geo_loc[0])) #latitude
            output.append(get_value(geo_loc[1])) #longitude
        else:
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
