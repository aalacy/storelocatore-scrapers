import csv
import re
import pdb
import requests
from lxml import etree
import json
import ast

base_url = 'http://zultimate.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "http://zultimate.com/locations"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    link_list = response.xpath('//ul[@class="locations-list"]//a/@href')
    for link in link_list:
        data = etree.HTML(session.get(link).text)     
        store = json.loads(validate(data.xpath('.//script[@class="yoast-schema-graph yoast-schema-graph--main"]//text()')))['@graph']
        output = []
        output.append(base_url) # url
        output.append(get_value(store[0]['name'])) #location name
        if len(store) > 3:
            store = store[5]
            output.append(get_value(store['address']['streetAddress'])) #address
            output.append(get_value(store['address']['addressLocality'])) #city
            output.append(get_value(store['address']['addressRegion'])) #state
            output.append(get_value(store['address']['postalCode'])) #zipcode
            output.append('US') #country code
            output.append('<MISSING>') #store_number
            output.append(get_value(store['telephone'])) #phone
            output.append('Best Martial Arts Lessons & Karate Classes for Self Defense') #location type
            output.append(get_value(store['geo']['latitude'])) #latitude
            output.append(get_value(store['geo']['longitude'])) #longitude
            store_hours = []
            if store['openingHoursSpecification']:
                for hour in store['openingHoursSpecification']:
                    for day in hour['dayOfWeek']:
                        store_hours.append(day + ' ' + hour['opens']+'-'+hour['closes'])
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
