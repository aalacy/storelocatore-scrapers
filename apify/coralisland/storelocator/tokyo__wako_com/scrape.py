import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.tokyo-wako.com'

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
    url = "https://www.tokyo-wako.com"
    session = requests.Session()
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    source = session.get(url,  headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//ul[@class="dropdown-menu dropdown-menu-left"]//a/@href')
    for store_link in store_list:
        store_link = base_url + '/' + store_link
        store = etree.HTML(session.get(store_link, headers=headers).text)
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath('.//div[@class="About-Us-main-box"]//h2//text()'))) #location name
        detail = eliminate_space(store.xpath('.//div[@class="About-Us-main-box"]//p[@class="wow fadeInLeft"]')[0].xpath('.//text()'))
        output.append(detail[0]) #address
        address = eliminate_space(detail[1].replace(',','').strip().split(' '))
        output.append(validate(address[:-2])) #city
        output.append(address[-2]) #state
        output.append(address[-1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(detail[2]) #phone
        output.append("Tokyo Wako") #location type
        output.append("<INACCESSIBLE>") #latitude
        output.append("<INACCESSIBLE>") #longitude
        store_hours = eliminate_space(store.xpath('.//div[@class="About-Us-main-box"]//p[@class="wow fadeInLeft"]')[-1].xpath('.//text()'))
        output.append(get_value(', '.join(store_hours))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
