import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.signsnow.com'

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
    url = "https://www.signsnow.com/all-locations"
    history = []
    page_url = ''
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="innerbody"]//a/@href')
    for store_link in store_list:
        if store_link != '#' and store_link not in history:
            history.append(store_link)
            if 'http' not in store_link:
                store_link = base_url + store_link
            store = etree.HTML(session.get(store_link).text)
            output = []
            output.append(base_url) # url
            output.append(store_link) # page url
            output.append(get_value(store.xpath('.//p[@class="location-name"]//text()'))) #location name
            address = eliminate_space(store.xpath('.//p[@class="contact"]//text()'))[1:]
            if address[-1][-2:] != 'GB':
                if address[-1][-2:] != 'CA':
                    address = parse_address(', '.join(address))
                    output.append(address['street']) #address
                    output.append(address['city']) #city
                    output.append(address['state']) #state
                    output.append(address['zipcode']) #zipcode  
                    output.append('US') #country code
                else:
                    try:
                        output.append(address[0]) #address
                        city_statezip = address[1].split(', ')
                        output.append(city_statezip[0]) #city
                        state_zip = eliminate_space(city_statezip[1].split(' '))
                        output.append(state_zip[0]) #state
                        output.append(validate(state_zip[1:-1])) #zipcode  
                        output.append('CA') #country code
                    except:
                        pdb.set_trace()
                output.append("<MISSING>") #store_number
                output.append(get_value(store.xpath('.//p[@class="phone"]//text()'))) #phone
                output.append("Custom Made Signs, Banners, Displays, & Graphics") #location type
                output.append("<MISSING>") #latitude
                output.append("<MISSING>") #longitude
                output.append("<MISSING>") #opening hours
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
