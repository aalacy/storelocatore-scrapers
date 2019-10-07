import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://www.sweatybetty.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip().replace('\n', '')

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
        if item != '' and item != 'USA':
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
    url = "https://www.sweatybetty.com/shop-finder"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="small-12 medium-4 columns store-column"]')[-1].xpath('.//a[@class="store-link"]/@href')
    for store_link in store_list:
        store_link = base_url + store_link
        store = etree.HTML(session.get(store_link).text)
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        store_hours = []
        days = eliminate_space(store.xpath('.//div[@class="store-hours"]//div[@class="medium-3 show-for-medium columns"]//text()'))
        hours = eliminate_space(store.xpath('.//div[@class="store-hours"]//div[@class="small-12 medium-9 columns"]//text()'))
        for idx, day in enumerate(days):
            store_hours.append(day + ' ' + hours[idx])
        if len(store_hours) > 0:
            output.append(validate(store.xpath('.//h1//text()'))) #location name
            details = eliminate_space(store.xpath('.//div[contains(@class, "main-details")]')[0].xpath('./text()'))
            address = ', '.join(details[:-1])
            address = parse_address(address)
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(details[-1]) #phone
            output.append("Sweaty Betty") #location type
            geo_loc = validate(store.xpath('.//div[@class="open-in-maps"]//a/@href')).split('q=')
            if len(geo_loc) > 0:
                geo_loc = geo_loc[1].split('&')[0].split(',')
                output.append(geo_loc[0]) #latitude
                output.append(geo_loc[1]) #longitude
            else:
                output.append("<MISSING>") #latitude
                output.append("<MISSING>") #longitude
            output.append(get_value(store_hours)) #opening hours            
            output_list.append(output)
        else:
            output.append(validate(store.xpath('.//h1//text()'))) #location name
            details = eliminate_space(store.xpath('.//div[contains(@class, "store-details-copy")]/p//text()'))
            address = ', '.join(details[1:-1]).replace('Shopping Center', '')
            address = parse_address(address)
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(details[-1]) #phone
            output.append("Sweaty Betty") #location type
            detail_link = validate(store.xpath('.//div[contains(@class, "store-details-copy")]//a/@href'))
            more_info = session.get(detail_link).text
            store_hours = eliminate_space(etree.HTML(more_info).xpath('.//div[contains(@class, "_13CMA _1JtW7 _2VF_A _2wqvV")]//text()'))
            geo_loc = more_info.split('"latitude":')[1].split(',"amenities"')[0].split(',"longitude":')
            if len(geo_loc) > 0:
                output.append(geo_loc[0]) #latitude
                output.append(geo_loc[1]) #longitude
            else:
                output.append("<MISSING>") #latitude
                output.append("<MISSING>") #longitude
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
