import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.honolulucookie.com'

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
    url = "https://www.honolulucookie.com/content/store-locations.asp"
    page_url = ''
    session = requests.Session()
    source = session.get(url).text
    # with open('res.text', 'wb') as f:
    #     f.write(source.encode('utf8'))
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="location-section"]//ul')[3:]
    for store in store_list:
        store_link = validate(store.xpath('.//a/@href'))
        if 'http' not in store_link:
            store_link = base_url + '/' + store_link
        more_info = etree.HTML(session.get(store_link).text)
        details = eliminate_space(store.xpath('.//li/text()'))
        address = ''
        phone = ''
        store_hours = []
        for idx, de in enumerate(details):
            if ':' in de.lower():
                address = ', '.join(details[:idx])
                phone = validate(de.split(':')[1])
                if 'fax' in details[idx+1].lower():
                    store_hours = validate(details[idx+2:])
                else:
                    store_hours = validate(details[idx+1:])
                break
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(get_value(store.xpath('.//a//text()'))) #location name
        address = parse_address(address)
        if address['zipcode'] == '<MISSING>':
            details = eliminate_space(more_info.xpath('.//div[@class="wpc_page_content"]//ul//text()'))
            address = ''
            for idx, de in enumerate(details):
                if ':' in de.lower():
                    address = details[idx-2].replace(',', '') + ', ' + details[idx-1].replace(',', '')
                    break            
            address = parse_address(address)
            output.append(address['street']) #address
            output.append('Honolulu') #city
            output.append('HI') #state
            output.append(address['zipcode']) #zipcode  
        else:
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(phone)) #phone
        output.append("Honolulu Cookie Company") #location type
        geo_loc = validate(more_info.xpath('.//div[@class="wpc_page_content"]/p//a/@href')).split('?ll=')
        if len(geo_loc) > 1:
            geo_loc = geo_loc[1].split('&')[0].split(',')
            output.append(get_value(geo_loc[0])) #latitude
            output.append(get_value(geo_loc[1])) #longitude
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
