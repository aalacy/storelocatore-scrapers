import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://labambaburritos.com/location'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').replace('\t', '').strip()

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
    url = "http://labambaburritos.com/location"
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': 'tk_ai=woo%3ADby8FT5b6LlA19EGu8q3F8qN',
        'Host': 'labambaburritos.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[contains(@class, "vc_tta-panels")]/div')
    for store in store_list:
        details = eliminate_space(store.xpath('.//div[contains(@class, "trx_addons_columns_wrap")]')[0].xpath('.//text()'))        
        output = []
        output.append(base_url) # url
        output.append(url) # page url
        address = details[2].strip().split(',')
        output.append(address[0] + ', ' + address[1].strip().split(' ')[0]) #location name
        output.append(details[1]) #address
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(details[3])) #phone
        output.append("La Bamba Burritos | Mexican Restaurants") #location type        
        geo_loc = eliminate_space(validate(store.xpath('.//div[@class="wpb_map_wraper"]')[0].xpath('./iframe/@src')).split('!2d')[1].split('!2m')[0].split('!3d'))
        output.append(geo_loc[1]) #latitude
        output.append(geo_loc[0]) #longitude
        output.append(get_value(details[5:])) #opening hours
        output_list.append(output)
        print(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
