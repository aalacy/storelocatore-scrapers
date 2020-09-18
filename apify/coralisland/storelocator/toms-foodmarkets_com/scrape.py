import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.toms-foodmarkets.com'

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
    url = "https://www.toms-foodmarkets.com/market-locator"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="locations"]')
    for store in store_list:        
        output = []
        output.append(base_url) # url
        loc_name = validate(store.xpath('.//h2//text()'))
        if loc_name != '':
            output.append(get_value(loc_name)) #location name
            detail = eliminate_space(store.xpath('.//p/text()'))
            hour_point = 0
            for idx, de in enumerate(detail):
                if 'hours:' in de.lower():
                    hour_point = idx
                    break
            store_hours = ', '.join(detail[hour_point:])
            detail = detail[:hour_point]
            output.append(', '.join(detail[:-2])) #address
            address = detail[-2].strip().split(',')
            output.append(address[0]) #city
            output.append(address[1].strip().split(' ')[0]) #state
            output.append(address[1].strip().split(' ')[1]) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(detail[-1]) #phone
            output.append("Tom's Food Markets") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            output.append(store_hours) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
