import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.freshtoorder.com'

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
    url = "https://www.freshtoorder.com/locate/"
    request = requests.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[contains(@class, "mpfy-mll-location")]')
    for store in store_list:
        info = validate(store.xpath('.//div[contains(@class, "location-address")]//text()')).split('|')
        street = info[0]
        info = info.pop().split(',')
        hours = get_value(eliminate_space(store.xpath('.//div[contains(@class, "location-hours")]//text()'))).replace('\n', '').replace('Restaurant Hours: ', '').replace('OPEN NOW!!! ', '')
        if 'Closed'in hours:
            continue
        output = []
        output.append(base_url) # url
        output.append(validate(store.xpath(".//div[@class='mpfy-mll-l-title']/text()"))) #location name
        output.append(validate(street)) #address
        output.append(info[0]) #city
        output.append(info[1]) #state
        output.append(info[2]) #zipcode
        output.append('US') #country code
        output.append(validate(store.xpath('./@data-id'))) #store_number
        output.append(get_value(store.xpath('.//div[contains(@class, "contact-details")]//text()'))) #phone
        output.append("Fresh To Order") #location type
        output.append(validate(store.xpath('./@data-lat'))) #latitude
        output.append(validate(store.xpath('./@data-lng'))) #longitude
        output.append(hours) #opening hours
        output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
