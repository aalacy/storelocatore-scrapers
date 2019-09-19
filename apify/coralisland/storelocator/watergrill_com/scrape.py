import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'http://watergrill.com/'

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
    url = "http://watergrill.com/"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="w-hidden-small w-hidden-tiny"]//a/@href')
    for store_link in store_list:
        try:
            store_link = base_url + store_link
            store = etree.HTML(session.get(store_link).text)
            detail = store.xpath('.//div[@class="address"]//text()')[0].encode("utf8").split('\xc3\xa2\xc2\x80\xc2\xa2 \xc3\x82\xc2\xa0')
            address = parse_address(validate(store.xpath('.//div[@class="address"]//text()')).replace(detail[1], ''))            
            output = []
            output.append(base_url) # url
            output.append('<MISSING>') #location name
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode   
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(get_value(detail[1])) #phone
            output.append("Water Grill") #location type
            geo_loc = validate(store.xpath('.//a[contains(@class, "footer-link directions-link")]/@href')).split('/@')[1].split(',15z')[0].split(',')
            output.append(geo_loc[0]) #latitude
            output.append(geo_loc[1]) #longitude
            hours_link = base_url + validate(store.xpath('.//a[contains(@class, "footer-link info-link")]//@href')).replace('../', '')
            store_hours = validate(etree.HTML(session.get(hours_link).text).xpath('//div[@class="row-reservations w-row"]//div[contains(@class, "column-info")]/div')[-1].xpath('.//text()')).replace('\xc3\xa2\xc2\x80\xc2\x8d', '')
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
        except Exception as e:
            pdb.set_trace()
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
