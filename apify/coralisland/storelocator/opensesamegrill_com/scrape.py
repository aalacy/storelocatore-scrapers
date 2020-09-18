import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.opensesamegrill.com'

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
    url = "https://www.opensesamegrill.com"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = json.loads(validate(response.xpath('.//script[@type="application/ld+json"]//text()')[0]))['subOrganization']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['name'])) #location name
        output.append(get_value(store['address']['streetAddress'])) #address
        output.append(get_value(store['address']['addressLocality'])) #city
        output.append(get_value(store['address']['addressRegion'])) #state
        output.append(get_value(store['address']['postalCode'])) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['telephone'])) #phone
        output.append(get_value(store['@type'])) #location type
        output.append('<INACCESSIBLE>') #latitude
        output.append('<INACCESSIBLE>') #longitude
        store_hours = eliminate_space(etree.HTML(session.get(validate(store['url'])).text).xpath('.//section[@id="intro"]//p')[-1].xpath('.//text()'))
        output.append(get_value(','.join(store_hours))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
