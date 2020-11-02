import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.yoursterlingpharmacy.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.yoursterlingpharmacy.com/locations"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="location-directory-services"]')
    for store_link in store_list:
        store_link = base_url + validate(store_link.xpath('.//a/@href')[0])
        store = etree.HTML(session.get(store_link).text)
        output = []
        detail = validate(store.xpath('.//div[@class="location-header-info__address"]/a/@href'))
        output.append(base_url) # url
        output.append(validate(store.xpath('.//a[@class="title"]//text()'))) #location name
        address = eliminate_space(detail.split('?q=')[1].split('+U.S')[0].replace('+', ' ').split('%2C'))
        street = validate(address[:-3])
        for addr in address[-3:]:
            street = street.replace(addr, '')
        output.append(street) #address
        output.append(validate(address[-3])) #city
        output.append(validate(address[-2])) #state
        output.append(validate(address[-1])) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(validate(store.xpath('.//div[@class="location-header-info__phone"]//text()'))) #phone
        output.append("Sterling cultivates Pharmacy") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        store_hours = validate(store.xpath('.//ol[@class="location-header-info__hours-list"]//text()'))
        output.append(get_value(store_hours)) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
