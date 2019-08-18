import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.firenzapizza.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").replace('&nbsp;', '').strip()

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
    url = "https://www.firenzapizza.com/location-store-locator/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = json.loads(validate(response.xpath('//script[@type="application/ld+json"]//text()')))['subOrganization']    
    for store in store_list[:-1]:
        output = []        
        output.append(base_url) # url
        output.append(store['name']) #location name
        output.append(store['address']['streetAddress']) #address
        output.append(store['address']['addressLocality']) #city
        output.append(store['address']['addressRegion']) #state
        output.append(store['address']['postalCode']) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['telephone'])) #phone
        output.append(store['@type']) #location type
        output.append('<MISSING>') #latitude
        output.append('<MISSING>') #longitude
        output.append(get_value(store['description'])) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
