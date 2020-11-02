import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree

base_url = 'https://prestopasta.com'

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
        if item != '' and 'order' not in item.lower() and item != ')':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://prestopasta.com/locations/"
    session = session = SgRequests()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@id="inner-content"]/p')
    for store in store_list:
        store = eliminate_space(store.xpath('.//text()'))
        if store[1] == "Or":
            del store[1:4]
        if store[1] == "See Menu":
            store.pop(1)
        output = []
        output.append(base_url) # url
        output.append(url)
        output.append(store[0].replace('\xa0','').replace('(', '').strip()) #location name
        output.append(store[1]) #address
        address = store[2].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        phone = ''
        store_hours = ''
        for idx, st in enumerate(store):
            if ')' in st and '-' in st :
                phone = st
                store_hours = ', '.join(store[idx+1:])
                break
        output.append(get_value(phone)) #phone
        output.append("<MISSING>") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
