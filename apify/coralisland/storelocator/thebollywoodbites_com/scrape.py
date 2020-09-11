import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.thebollywoodbites.com'

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
    url = "https://www.thebollywoodbites.com/contact-us/"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',        
        'cookie': 'PHPSESSID=3bce368d184f817b2a491afa09a2db32; gwcc=%7B%22expires%22%3A86400%2C%22backoff_expires%22%3A1573209697%7D; _sp_ses.204f=*; _sp_id.204f=c9d28760-9318-4234-93ea-5feb77b9629c.1568632335.6.1573123620.1572974956.1b387353-5b52-431d-83ba-de147d658429',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36'
    }
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="wpb_column vc_column_container vc_col-sm-3"]')
    for store in store_list:
        geo_loc = validate(store.xpath('.//div[@class="wpb_map_wraper"]//iframe/@src')).split('!2d')[1].split('!3m')[0].split('!3d')
        store = eliminate_space(store.xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(url) # page url
        address = store[1].strip().split(',')
        output.append(address[0]) #location name
        output.append(get_value(address[1])) #address
        output.append(address[2]) #city
        output.append(address[3].strip().split('-')[0]) #state
        output.append(address[3].strip().split('-')[1]) #zipcode        
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[-1]) #phone
        output.append("Bollywood Bites Best Indian Restaurant in LA & Sherman Oaks") #location type
        output.append(geo_loc[1]) #latitude
        output.append(geo_loc[0]) #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
