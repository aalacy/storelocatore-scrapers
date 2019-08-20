import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.yiayiamarys.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

def get_value(item):
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
    url = "https://www.yiayiamarys.com"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('.//div[@class="col sqs-col-6 span-6"]')[1].xpath('.//div[@class="row sqs-row"]')
    for store in store_list:        
        store_hours = validate(store.xpath('.//div[@class="sqs-block html-block sqs-block-html"]//p')[1].xpath('.//text()')).split(':')[1].strip()
        detail = eliminate_space(store.xpath('.//div[@class="sqs-block html-block sqs-block-html"]//p')[0].xpath('.//text()'))
        store = json.loads(store.xpath('.//div[@class="sqs-block map-block sqs-block-map"]//@data-block-json')[0])['location']
        output = []
        output.append(base_url) # url
        output.append(detail[0]) #location name
        output.append(store['addressLine1']) #address
        address = eliminate_space(store['addressLine2'].replace(',', '').strip().split(' '))        
        output.append(address[0]) #city
        output.append(address[1]) #state
        output.append(address[2]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(detail[3]) #phone
        output.append(store['addressTitle']) #location type        
        output.append(store['mapLat']) #latitude
        output.append(store['mapLng']) #longitude
        output.append(store_hours) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
