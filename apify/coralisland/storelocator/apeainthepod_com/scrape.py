import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.apeainthepod.com'

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
            if len(row) > 0:
                writer.writerow(row)

def parse_detail(store, link, number):
    output = []
    output.append(base_url) # url
    output.append(get_value(store.xpath('.//h1[@class="Core-title"]//text()')))#location name
    output.append(get_value(store.xpath('.//div[@class="Core-address"]//span[@class="c-address-street-1"]//text()'))) #address    
    output.append(get_value(store.xpath('.//div[@class="Core-address"]//span[@class="c-address-city"]//text()')).replace(',', '')) #city
    output.append(get_value(store.xpath('.//div[@class="Core-address"]//abbr[@itemprop="addressRegion"]//text()'))) #state
    output.append(get_value(store.xpath('.//div[@class="Core-address"]//span[@itemprop="postalCode"]//text()'))) #zipcode
    output.append('US') #country code
    output.append("<MISSING>") #store_number
    output.append(get_value(store.xpath('.//div[@itemprop="telephone"]//text()'))) #phone
    output.append("Stylish Maternity Clothes + Designer Fashions") #location type
    output.append('<MISSING>') #latitude
    output.append('<MISSING>') #longitude
    output.append(get_value(eliminate_space(store.xpath('.//table[@class="c-hours-details"]//tbody//text()')))) #opening hours
    return output

def fetch_data():
    output_list = []
    url = "https://stores.apeainthepod.com/us"
    session = requests.Session()
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    request = session.get(url)
    response = etree.HTML(request.text) 
    state_list = response.xpath('//div[@class="Directory-content"]//a[@class="Directory-listLink"]/@href')
    url = 'https://stores.apeainthepod.com/'
    for state in state_list:
        state = url + state.replace('../', '')
        state_response = etree.HTML(session.get(state, headers=headers).text)
        if state_response is not None:
            city_list = state_response.xpath('//div[@class="Directory-content"]//a[@class="Directory-listLink"]/@href')
            store_list = state_response.xpath('//div[@class="Directory-content"]//a[@class="Teaser-titleLink"]/@href')
            if len(city_list) > 0:                
                for city in city_list:
                    city = url + city.replace('../', '')
                    city_response = etree.HTML(session.get(city, headers=headers).text)
                    if city_response is not None:
                        store_list = city_response.xpath('//div[@class="Directory-content"]//a[@class="Teaser-titleLink"]/@href')
                        if len(store_list) > 0:
                            for store in store_list:
                                store = url + store.replace('../', '')
                                store_response = etree.HTML(session.get(store, headers=headers).text)
                                if store_response is not None:
                                    output_list.append(parse_detail(store_response, store, '1'))
                        else:
                            output_list.append(parse_detail(city_response, city, '2'))
            elif len(store_list) > 0:   
                for store in store_list:
                    store = url + store.replace('../', '')
                    store_response = etree.HTML(session.get(store, headers=headers).text)
                    if store_response is not None:                        
                        output_list.append(parse_detail(store_response, store, '3'))
            else:
                output_list.append(parse_detail(state_response, state, '4'))
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
