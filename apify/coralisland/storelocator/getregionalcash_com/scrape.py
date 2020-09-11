import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.regionalfinance.com'

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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def parse_detail(store, link, level=0):    
    output = []
    output.append(base_url) # url
    output.append(link) # url
    output.append(get_value(store.xpath('.//h1[@class="LocationInfo-title"]//text()')))#location name
    output.append(get_value(store.xpath('.//span[@itemprop="streetAddress"]//text()'))) #address    
    output.append(get_value(store.xpath('.//span[@itemprop="addressLocality"]//text()')).replace(',', '')) #city
    output.append(get_value(store.xpath('.//abbr[@itemprop="addressRegion"]//text()'))) #state
    output.append(get_value(store.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
    output.append('US') #country code
    output.append("<MISSING>") #store_number
    output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
    output.append("Regional Finance") #location type
    output.append(get_value(store.xpath('.//div[@class="LocationInfo-map"]//meta[@itemprop="latitude"]/@content'))) #latitude
    output.append(get_value(store.xpath('.//div[@class="LocationInfo-map"]//meta[@itemprop="longitude"]/@content'))) #longitude
    output.append(get_value(eliminate_space(store.xpath('.//table[@class="c-location-hours-details"]//tbody//text()')))) #opening hours
    return output

def fetch_data():
    output_list = []
    url = "https://www.regionalfinance.com/locations"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }    
    request = session.get(url, headers=headers)    
    response = etree.HTML(request.text)    
    state_list = response.xpath('//section[@id="choose-branch"]/p//a/@href')
    url = 'https://branches.regionalfinance.com/'
    for state in state_list:        
        state_response = etree.HTML(session.get(state, headers=headers).text)
        if state_response is not None:
            city_list = state_response.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
            store_list = state_response.xpath('//a[@data-ya-track="visitsite"]/@href')
            if len(city_list) > 0:
                for city in city_list:
                    city = url + city
                    city_response = etree.HTML(session.get(city, headers=headers).text)
                    if city_response is not None:
                        store_list = city_response.xpath('//a[@data-ya-track="visitsite"]/@href')
                        if len(store_list) > 0:
                            for store in store_list:
                                store = url + store.replace('../', '')
                                store_response = etree.HTML(session.get(store, headers=headers).text)
                                if store_response is not None:
                                    output_list.append(parse_detail(store_response, store))
                        else:                            
                            output_list.append(parse_detail(city_response, city))
            elif len(store_list) > 0:
                for store in store_list:
                    store = url + store.replace('../', '')
                    store_response = etree.HTML(session.get(store, headers=headers).text)
                    if store_response is not None:
                        output_list.append(parse_detail(store_response, store))
            else:
                output_list.append(parse_detail(state_response, state))
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
