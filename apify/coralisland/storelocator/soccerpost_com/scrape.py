import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.soccerpost.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').replace('\n', '').encode("utf8").strip()

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

def parse(item, reg):
    return item.split(reg+':')[1].split(',')[0].replace('"', '') .strip()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.soccerpost.com"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    data = validate(response.xpath('.//script[@type="text/javascript"]')[-1].xpath('.//text()'))
    store_list = data.split('SP.stores = [{')[1].split('}];//]]>')[0].split('},{')
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(parse(store, 'name')) #location name
        output.append(parse(store, 'address')) #address        
        output.append(parse(store, 'city')) #city
        output.append(parse(store, 'state')) #state
        output.append(parse(store, 'zip')) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(parse(store, 'phone')) #phone
        output.append("Soccer Post America's Soccer Store") #location type
        output.append(parse(store, 'latitude')) #latitude
        output.append(parse(store, 'longitude')) #longitude
        output.append("<MISSING>") #opening hours   
        # if parse(store, 'url') != '':
        #    res = etree.HTML(session.get(parse(store, 'url')).text)
        #    store_hours = validate(eliminate_space(res.xpath('//div[@class="pp-sub-heading"]')[1].xpath('.//text()')))
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
