import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://arbys.com'

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

def parse_detail(store, link):
    output = []
    output.append(base_url) # url
    output.append(get_value(store.xpath('.//h1[@class="c-location-title"]//text()')))#location name
    output.append(get_value(store.xpath('.//span[@itemprop="streetAddress"]//text()'))) #address    
    output.append(get_value(store.xpath('.//span[@itemprop="addressLocality"]//text()')).replace(',', '')) #city
    output.append(get_value(store.xpath('.//abbr[@itemprop="addressRegion"]//text()'))) #state
    output.append(get_value(store.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
    country = eliminate_space(link.split('/'))[2].upper()
    output.append(country) #country code
    output.append(get_value(store.xpath('.//div[@class="logistics-detail-store-id hidden-xs hidden-sm"]//text()')).split('#')[-1]) #store_number
    output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
    output.append("Arby's Restaurants") #location type
    geo = validate(store.xpath('.//link[@itemprop="map"]//@href')).split('center=')[1].split('&channel')[0].split('%2C')
    output.append(geo[0]) #latitude
    output.append(geo[1]) #longitude
    output.append(get_value(eliminate_space(store.xpath('.//table[@class="c-location-hours-details"]//tbody//text()')))) #opening hours
    if 'Coming Soon' not in output[1] and 'Closed' not in output[1]:
        return output
    else:
        return []

def fetch_data():
    output_list = []
    url = "https://locations.arbys.com/"
    locator_url = 'https://locations.arbys.com/'
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '__cfduid=d9fe2173d819944df870fdd282a72726f1566644990',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    state_list = response.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
    for state in state_list:
        state = locator_url + state.replace('../', '')
        state_response = etree.HTML(session.get(state, headers=headers).text)
        if state_response is not None:
            city_list = state_response.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
            store_list = state_response.xpath('//a[@class="c-location-grid-item-link c-location-grid-item-link-visitpage"]/@href')
            if len(city_list) > 0:
                for city in city_list:
                    city = locator_url + city.replace('../', '')
                    city_response = etree.HTML(session.get(city, headers=headers).text)
                    if city_response is not None:
                        store_list = city_response.xpath('//a[@class="c-location-grid-item-link c-location-grid-item-link-visitpage"]/@href')
                        if len(store_list) > 0:
                            for store in store_list:
                                store = locator_url + store.replace('../', '')
                                store_response = etree.HTML(session.get(store, headers=headers).text)                                
                                if store_response is not None:
                                    output_list.append(parse_detail(store_response, store))
                        else:
                            output_list.append(parse_detail(city_response, city))
            elif len(store_list) > 0:
                for store in store_list:
                    store = locator_url + store.replace('../', '')
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
