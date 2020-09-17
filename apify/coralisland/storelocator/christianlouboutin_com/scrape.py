import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://us.christianlouboutin.com'

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
    session = requests.Session()    
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Cookie': 'is_mobile=no; is_mobile=no; is_mobile=no; liveagent_oref=; newCountry=International; visited=1; liveagent_ptid=a686ab3d-9fe5-4f11-bace-af5a518091b5; LAST_CATEGORY=4; CATEGORY_INFO=%5B%5D; CACHED_FRONT_FORM_KEY=YLE2GaRTVGEsjSXg; resolution=1366; liveagent_sid=f36157bb-e4a4-4768-ae42-fbb594e248b9; liveagent_vc=5; oldCountry=Cambodia; country=Cambodia; index_empty_modal=1; frontend=nti0mebe41u19up02nv6ipdv51; country_empty_modal=1; newsletter_popup=1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    }
    source = session.get('http://us.christianlouboutin.com/ot_en/storelocator/north-america/united-states').text
    response = etree.HTML(source)
    store_list = eliminate_space(response.xpath('//a[@class="item"]/@href'))
    for store_link in store_list:
        if 'http' not in store_link:
            store_link = base_url + store_link
        store = etree.HTML(session.get(store_link).text)
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(get_value(store.xpath('.//div[@id="store-information"]//htag1[@itemprop="name"]//text()'))) #location name
        city = get_value(store.xpath('.//div[@id="store-information"]//span[@class="city"]//text()'))
        zipcode = eliminate_space(get_value(store.xpath('.//div[@id="store-information"]//span[@class="address2"]//text()')).replace(city, '').replace(',', '').replace('US', '').split(' '))
        if len(zipcode) > 1:
            if 'floor' in zipcode:
                output.append(get_value(store.xpath('.//div[@id="store-information"]//span[@class="address1"]//text()') + ' ' + zipcode)) #address
                output.append(city) #city
                output.append('<MISSING>') #state
                output.append('<MISSING>') #zipcode
            else:
                output.append(get_value(store.xpath('.//div[@id="store-information"]//span[@class="address1"]//text()'))) #address            
                output.append(city) #city
                output.append(zipcode[0]) #state
                output.append(validate(zipcode[1:])) #zipcode
        else:
            output.append(get_value(store.xpath('.//div[@id="store-information"]//span[@class="address1"]//text()'))) #address            
            output.append(city) #city
            output.append('<MISSING>') #state
            output.append(validate(zipcode)) #zipcode             
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//div[@id="store-information"]//span[@itemprop="telephone"]//text()'))) #phone
        output.append("Christian Louboutin Official Boutique") #location type
        output.append("<INACCESSIBLE>") #latitude
        output.append("<INACCESSIBLE>") #longitude
        store_hours = eliminate_space(store.xpath('.//div[@class="col col-1"]//div[@class="hours"]//text()'))
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)     

    source = session.get('http://us.christianlouboutin.com/ot_en/storelocator/north-america/canada').text
    response = etree.HTML(source)
    store_list = eliminate_space(response.xpath('//a[@class="item"]/@href'))
    for store_link in store_list:
        if 'http' not in store_link:
            store_link = base_url + store_link
        store = etree.HTML(session.get(store_link).text)
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(get_value(store.xpath('.//div[@id="store-information"]//htag1[@itemprop="name"]//text()'))) #location name
        city = get_value(store.xpath('.//div[@id="store-information"]//span[@class="city"]//text()'))
        zipcode = eliminate_space(get_value(store.xpath('.//div[@id="store-information"]//span[@class="address2"]//text()')).replace(city, '').replace(',', '').replace('CA', '').split(' '))
        if len(zipcode) > 2:
            output.append(get_value(store.xpath('.//div[@id="store-information"]//span[@class="address1"]//text()'))) #address            
            output.append(city) #city
            output.append(zipcode[0]) #state
            output.append(validate(zipcode[1:])) #zipcode
        else:
            output.append(get_value(store.xpath('.//div[@id="store-information"]//span[@class="address1"]//text()'))) #address            
            output.append(city) #city
            output.append('<MISSING>') #state
            output.append(validate(zipcode)) #zipcode  
        output.append('CA') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//div[@id="store-information"]//span[@itemprop="telephone"]//text()'))) #phone
        output.append("Christian Louboutin Official Boutique") #location type
        output.append("<INACCESSIBLE>") #latitude
        output.append("<INACCESSIBLE>") #longitude
        store_hours = eliminate_space(store.xpath('.//div[@class="col col-1"]//div[@class="hours"]//text()'))
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)            
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
