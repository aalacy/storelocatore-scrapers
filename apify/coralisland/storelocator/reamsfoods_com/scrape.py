import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://reamsfoods.com'

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
    url = "https://reamsfoods.com/locations/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[contains(@class, "et_pb_module et_pb_image")]//a/@href')
    for link in store_list:
        link = base_url + link
        store = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h1//text()'))) #location name
        store = store.xpath('.//div[@class="et_pb_module et_pb_text et_pb_text_2 et_pb_bg_layout_light  et_pb_text_align_left"]')[0]
        address = parse_address(get_value(store.xpath('.//address//text()')))
        output.append(address['street'])
        output.append(address['city'])
        output.append(address['state'])
        output.append(address['zipcode'])
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(eliminate_space(store.xpath('.//p//a/text()')) )) #phone
        detail = eliminate_space(store.xpath('.//p//text()'))
        start_point = 0
        end_point = len(detail)-1
        store_hours = ''
        for idx, de in enumerate(detail):
            if 'hours' in de.lower() and start_point == 0:
                start_point = idx
            if 'location' in de.lower() and end_point == len(detail)-1:
                end_point = idx
        store_hours = ' '.join(detail[start_point:end_point])
        output.append("Reams Food Store | Fresh Produce, Delicious Meats") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
