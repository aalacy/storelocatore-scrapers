import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.primroseschools.com'

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
    url = "https://www.primroseschools.com/locations/"
    session = requests.Session()
    headers={
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)    
    store_list = response.xpath('//a[@class="location-school"]/@href')
    for link in store_list:
        link = base_url + link
        store = etree.HTML(session.get(link, headers=headers).text)
        output = []            
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h1[@class="hero-content"]//text()'))) #location name
        output.append(get_value(store.xpath('.//article[@class="card card-address"]//span[@itemprop="streetAddress"]//text()'))) #address
        output.append(get_value(store.xpath('.//article[@class="card card-address"]//span[@itemprop="addressLocality"]//text()'))) #city
        output.append(get_value(store.xpath('.//article[@class="card card-address"]//span[@itemprop="addressRegion"]//text()'))) #state
        output.append(get_value(store.xpath('.//article[@class="card card-address"]//span[@itemprop="postalCode"]//text()'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//article[@class="card card-address"]//span[@itemprop="telephone"]//text()'))) #phone
        output.append('Primrose Schools') #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(get_value(store.xpath('.//article[@class="card card-address"]//span[@class="card-info-line"]//text()')[-1])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
