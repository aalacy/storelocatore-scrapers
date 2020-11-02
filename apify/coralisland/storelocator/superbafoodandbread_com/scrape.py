import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json
import unidecode

base_url = 'http://www.superbafoodandbread.com'

session = SgRequests()

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').strip()

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

def sanitize(s):
    return unidecode.unidecode(s)

def fetch_data():
    output_list = []
    url = "http://www.superbafoodandbread.com"
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="col sqs-col-4 span-4"]//div[@class="sqs-block html-block sqs-block-html"]')
    for store in store_list:
        details = eliminate_space(store.xpath('.//text()'))
        output = []
        if len(details) > 3:
            if "coming soon" in details[0].lower():
                continue
            geo_loc = validate(store.xpath('.//a/@href')).split('/@')[1].split(',17z')[0].split(',')
            output.append(base_url) # url
            output.append(sanitize(details[0])) #location name
            output.append(sanitize(details[2])) #address
            address = details[3].strip().split(',')
            output.append(sanitize(address[0])) #city
            output.append(sanitize(address[1].strip().split(' ')[0])) #state
            output.append(sanitize(address[1].strip().split(' ')[1])) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #details_number
            output.append(sanitize(details[4])) #phone
            output.append(sanitize(details[1])) #location type
            output.append(geo_loc[0]) #latitude
            output.append(geo_loc[1]) #longitude
            output.append(sanitize(validate(details[6:]))) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
