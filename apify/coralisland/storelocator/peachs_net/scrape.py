import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://www.peachs.net'

def validate(item):    
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
    url = "http://www.peachs.net/locations.html"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="uk-button uk-button-primary uk-button-small uk-margin-top"]//a/@href')
    for link in store_list:
        link = base_url + link
        store = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h1[@class="uk-text-orange uk-margin-top-remove"]//text()'))) #location name
        address = eliminate_space(store.xpath('.//ul[@class="uk-list"]//text()'))
        street = '<MISSING>'
        city = '<MISSING>'
        state = '<MISSING>'
        zipcode = '<MISSING>'
        phone = '<MISSING>'
        store_hours = '<MISSING>'
        for idx, addr in enumerate(address):
            if addr == 'Street:':
                street = address[idx+1]
            if addr == 'City:':
                city = address[idx+1]
            if addr == 'State:':
                state = address[idx+1]
            if addr == 'Zip Code:':
                zipcode = address[idx+1]
            if addr == 'Phone:':
                phone = address[idx+1]
            if addr == 'Hours:':
                store_hours = ', '.join(address[idx+1:])
        output.append(street) #address
        output.append(city) #city
        output.append(state) #state
        output.append(zipcode) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(phone) #phone
        output.append("Peach's Restaurants - Breakfast & Lunch in Sarasota, Bradenton") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(store_hours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
