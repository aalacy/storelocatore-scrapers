import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.woodysdiners.com'

def validate(item):    
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
    url = "https://www.woodysdiners.com/locations"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[contains(@class, "map-block sqs-block-map")]')
    store_hours = response.xpath('//div[@class="sqs-block html-block sqs-block-html"]//div[@class="sqs-block-content"]')[1:-1] 
    for idx, store in enumerate(store_list):
        store = json.loads(validate(store.xpath('./@data-block-json')))['location']
        detail = eliminate_space(store_hours[idx].xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(detail[0]) #location name
        output.append(store['addressLine1']) #address
        address = store['addressLine2'].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1]) #state
        output.append(address[2]) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(detail[3]) #phone
        output.append("Woody's Diners") #location type
        output.append(store['mapLat']) #latitude
        output.append(store['mapLng']) #longitude
        output.append(get_value(' '.join(detail[4:-2]).replace('Business Hours:', ''))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
