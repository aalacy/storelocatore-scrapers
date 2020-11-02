import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://paninisgrill.com'

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://paninisgrill.com/locations/"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    source = session.get(url, headers=headers).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="flip-box-back-inner"]')
    for store in store_list:
        link = eliminate_space(store.xpath('.//a/@href'))[0]
        output = []
        store_hours = ''
        if len(store) > 2 and '/' in link:
            link = base_url + link
            store = eliminate_space(store.xpath('.//text()'))            
            output.append(base_url) # url
            output.append(store[0]) #location name
            phone = ''
            for idx, st in enumerate(store[2:]):
                if '-' in st.lower():
                    address = store[2:idx+2]
                    phone = validate(st.replace('Phone:', ''))
                    break
            address = parse_address(validate(address).replace('Phone:', ''))
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(phone) #phone
            if address['street'] != '':
                hour_temp = etree.HTML(session.get(link, headers=headers).text).xpath('.//div[@class="fusion-text"]//p')
                for hour in hour_temp[2:]:
                    hour = validate(hour.xpath('.//text()'))
                    if 'event' not in hour.lower():
                        store_hours += hour + ' '
                store_hours = validate(store_hours)                
        else:
            phone = validate(store.xpath('.//p')[1].xpath('.//a//text()'))
            detail = eliminate_space(store.xpath('.//p')[0].xpath('.//text()'))
            output.append(base_url) # url
            if len(detail) > 0:
                output.append(detail[0]) #location name
                address = parse_address(validate(detail[2:]))
                output.append(address['street']) #address
                output.append(address['city']) #city
                output.append(address['state']) #state
                output.append(address['zipcode']) #zipcode  
            else:
                name = eliminate_space(store.xpath('.//a//text()'))
                output.append(name[0]) #location name
                output.append('<MISSING>') #address
                output.append('<MISSING>') #city
                output.append('<MISSING>') #state
                output.append('<MISSING>') #zipcode 
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(phone) #phone
        output.append("Panini's Bar & Grill") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(get_value(store_hours)) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
