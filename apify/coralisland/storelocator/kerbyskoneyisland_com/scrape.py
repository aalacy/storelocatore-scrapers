import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://kerbyskoneyisland.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

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
    url = "http://kerbyskoneyisland.com/locations.cfm"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="iEditPageBody"]/table')
    for store in store_list:        
        output = []
        output.append(base_url) # url
        title = get_value(store.xpath('.//h2//text()'))
        output.append(title) #location name
        detail_tmp = eliminate_space(store.xpath('.//table//text()'))
        detail = []
        for d in detail_tmp:
            if d == 'CLICK for MAP':
                break
            detail.append(d)
        if len(detail) > 0:
            if detail[0] == title:
                detail = detail[1:]
            output.append(' '.join(detail[:-2])) #address
            address = detail[-2].strip().split(',')
            output.append(address[0]) #city
            output.append(address[1].strip().split(' ')[0]) #state
            output.append(address[1].strip().split(' ')[1]) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(get_value(detail[-1].split(':')[1])) #phone
            output.append("Kerbys Koney Island") #location type
            output.append("<MISSING>") #latitude
            output.append("<MISSING>") #longitude
            store_hours = eliminate_space(store.xpath('./tr[1]//td[2]//text()'))
            output.append(', '.join(store_hours[1:])) #opening hours
            output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
