import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://newleaf.com'

def validate(str):
    ret = ' '.join(str).strip();
    if '-' in ret:
        ret = ret.split('-')[0].strip()
    return ret

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://newleaf.com/stores/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//ul[@id="locations-list"]//li')
    for store in store_list:        
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath('.//h3//text()'))) #location name
        detail = store.xpath('.//p')[0].xpath('.//text()')
        output.append(detail[0].strip()) #address
        address = detail[1].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(detail[2].split(':')[1].strip()) #phone
        output.append("Community Markets") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(detail[4].strip()) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
