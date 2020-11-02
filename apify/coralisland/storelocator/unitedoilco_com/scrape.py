import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://www.unitedoilco.com'

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
    url = "http://www.unitedoilco.com/locations"
    page_url = ''
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Cookie': 'PHPSESSID=5bcc9531684b20b2f442884d65b9ce98',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'
    }
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    brand_list = response.xpath('//div[@class="logos-location"]//a/@href')
    for brand in brand_list:
        brand_url = url + brand
        store_list = etree.HTML(session.get(brand_url, headers=headers).text).xpath('.//table')[1].xpath('.//tr')
        for store in store_list:
            page_url = validate(store.xpath('.//a/@href'))
            store = eliminate_space(store.xpath('.//text()'))
            output = []
            output.append(base_url) # url
            output.append(page_url) # page url
            output.append(store[0]) #location name
            output.append(store[1]) #address
            output.append(store[2]) #city
            output.append(store[3]) #state
            output.append(store[4]) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            phone = validate(etree.HTML(session.get(page_url, headers=headers).text).xpath('.//h1//text()')).split('Phone:')[-1].strip()
            output.append(get_value(phone)) #phone
            output.append("United Oil") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            output.append("<MISSING>") #opening hours
            output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
