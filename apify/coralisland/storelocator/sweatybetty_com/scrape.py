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
    return item.strip().replace('\n', '')

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
        title = validate(store.xpath('.//div[@class="store-details-title"]//text()'))
        output = []
        output.append(base_url) # url
        if title == '':
            output.append(validate(store.xpath('.//h1//text()'))) #location name
            detail = eliminate_space(store.xpath('.//div[contains(@class, "main-details")]')[0].xpath('./text()'))
            output.append(detail[0]) #address
            output.append(detail[1].split(',')[0]) #city
            output.append(detail[1].split(',')[1]) #state
            output.append(detail[2]) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(detail[3]) #phone
            output.append("Sweaty Betty") #location type
            geo_loc = validate(store.xpath('.//div[@class="open-in-maps"]//a/@href')).split('?q=')
            if len(geo_loc) > 1:
                geo_loc = geo_loc[1].split('&')[0].split(',')
                output.append(geo_loc[0]) #latitude
                output.append(geo_loc[1]) #longitude
            else:
                output.append("<MISSING>") #latitude
                output.append("<MISSING>") #longitude
            store_hours = eliminate_space(store.xpath('.//div[@class="store-hours"]//text()'))
            output.append(get_value(store_hours)) #opening hours
        else:
            try:
                output.append(title) #location name
                detail = eliminate_space(store.xpath('.//div[contains(@class, "store-details-copy")]//p[@class="copy"]//text()'))
                address = parse_address(', '.join(detail[1:-1]))
                output.append(address['street']) #address
                output.append(address['city']) #city
                output.append(address['state']) #state
                output.append(address['zipcode']) #zipcode  
                output.append('US') #country code
                output.append("<MISSING>") #store_number
                phone = validate(store.xpath('.//div[contains(@class, "store-details-copy")]//p[@class="phone"]//text()'))
                output.append(get_value(phone)) #phone
                output.append("Sweaty Betty") #location type
                more_info = etree.HTML(session.get(validate(store.xpath('.//div[@class="store-details-copy"]//a/@href'))).text)
                output.append("<MISSING>") #latitude
                output.append("<MISSING>") #longitude
                store_hours = eliminate_space(more_info.xpath('.//div[@class=" _13CMA _1JtW7 _2VF_A _2wqvV"]//text()'))
                output.append(get_value(store_hours)) #opening hours
            except Exception as e:
                pass
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
