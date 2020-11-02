import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.anntaylor.com'

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

def parse_detail(store, link):
    output = []
    output.append(base_url) # url
    output.append(get_value(store.xpath('.//h1[@class="c-location-title"]//text()')))#location name
    output.append(get_value(store.xpath('.//span[@itemprop="streetAddress"]//text()'))) #address    
    output.append(get_value(store.xpath('.//span[@itemprop="addressLocality"]//text()')).replace(',', '')) #city
    output.append(get_value(store.xpath('.//span[@itemprop="addressRegion"]//text()'))) #state
    output.append(get_value(store.xpath('.//span[@itemprop="postalCode"]//text()'))) #zipcode
    output.append('US') #country code
    output.append("<MISSING>") #store_number
    output.append(get_value(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
    output.append("ANN TAYLOR") #location type
    geo = validate(store.xpath('.//link[@itemprop="map"]//@href')).split('center=')[1].split('&channel')[0].split('%2C')
    output.append(geo[0]) #latitude
    output.append(geo[1]) #longitude
    output.append(get_value(eliminate_space(store.xpath('.//table[@class="c-location-hours-details"]')[0].xpath('.//text()')))) #opening hours
    return output

def fetch_data():
    output_list = []
    url = "https://stores.anntaylor.com"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': 'AKA_FEO=FALSE; s_fid=0267F8F57FF1F9F0-2D901D3F0DB514EF; cmgvo=Typed%2FBookmarkedTyped%2FBookmarkedundefined; s_cc=true; _abck=4EF34D9D95BBD5AAEA2B17F32753104E~0~YAAQT5TerRLef6JsAQAAaDvsswLamfqRFyRc5ELt4wDP2Mr5kqxCQZmRN5Ls7sk0F9ZQruIhKQdAzcRp0/O4Y6P3kjorKzog4hI9ptRfIuGAkD07x+vxKoKHlJZewZ6nBw2MHyPgNW+vRbeey1UjUVrjWp4VxbRMy3iy4EkwVBWW2Wuazycz9rbyjqO/4kRtJ8JWS9SDTlhHolcy+3e9uFF8pHILSwdcXsYkS9AO+CZ5cgXAhxQcgikV/qqUp6IyDm0/ddiO/BxGhGBoqIyNTUhBadlQIRdhOagOoahpVW15TXOcuyrnT3pvGNs=~-1~-1~-1; __cfduid=d461e17a9d05b9ccaec2fa30bead1ce281566386704; ak_bmsc=308AE66EAA0DEFDB67B9FFA3F517E72F68788BBC65120000308D5E5DBEF76D53~plaH4TS/knttRli3EdF5AI4PhxKmHm1Z3eepuFFBAIYe3b0rP+fODrT/BfOFEK78cL6wuPi3WLwCwIhxrthG8/H+tDW2JLhiUvLrhFATVIzxTzUexxjed3NFqhTmjAa22pP097douQZ0CBq9HUljD2RHtFYGdeuyF30jKXbi2B7y8/3SYos1YydBQYMTtb248uOBXX4xbPOGyonHazykTp77kRL6sVVs4ib3lAwgGyHcA=; bm_sz=FB558995A42E5A7C3688B355DCB5ED7B~YAAQvIt4aDDyerRsAQAAkoRXuQQ2qpll0CBsTS+pZg2qDgdATSjMjAUpeCLjRdRCLGbhZfciJIRnNYGA9vIuUs2XI7ORJk9VmbgG3O2A0hTiyml2yk6qpz0EPWgRBHzLnd6lKtguXmn7Lq12nMX0jRwFY2fYjT3cgoNwT1dk9AQwyWDdKDWx/dWca9Af6hNH8FUa; bm_sv=EF9BCA8A13872A47A0C9FC81A90AF16B~M1b0rY6rpmF9vM3vfFSzGsAXRUzmDH1IwEwiZwPgYfL3X3qF3UvL00G3GCUjqWBIejvimNoetVtokaS/GfIveefj3bPQmVvilhCxQePDxeAA1czr9BsZKVZdj5tgysHhEI2LikpX0VEsz4nF96TsuEVLPDDZwIY1/Z1BHeqzwfY=; s_sq=%5B%5BB%5D%5D; s_nr=1566478325014-Repeat; s_ppvl=StoreLocator%253Ama%2C89%2C89%2C821%2C1148%2C821%2C1366%2C768%2C0.8%2CP; s_ppv=StoreLocator%253Ama%2Flongmeadow%2F694-bliss-road%2C27%2C27%2C821%2C1148%2C821%2C1366%2C768%2C0.8%2CP',
        'if-modified-since': 'Sat, 17 Aug 2019 17:46:53 GMT',
        'if-none-match': '"346cdc7dad3aa83dc1c914efbf22b0b6"-gzip',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    url = 'https://stores.anntaylor.com'
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)    
    state_list = response.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
    for state in state_list:
        state = url + '/' + state
        state_response = etree.HTML(session.get(state, headers=headers).text)
        if state_response is not None:
            city_list = state_response.xpath('//a[@class="c-directory-list-content-item-link"]/@href')
            store_list = state_response.xpath('//a[@class="c-location-grid-item-link visit-page-YA"]/@href')
            if len(city_list) > 0:
                for city in city_list:
                    city = url + '/' + city
                    city_response = etree.HTML(session.get(city, headers=headers).text)
                    if city_response is not None:
                        store_list = city_response.xpath('//a[@class="c-location-grid-item-link visit-page-YA"]/@href')
                        if len(store_list) > 0:
                            for store in store_list:
                                store = url + store[2:]
                                store_response = etree.HTML(session.get(store, headers=headers).text)
                                if store_response is not None:
                                    output_list.append(parse_detail(store_response, store))
                        else:
                            output_list.append(parse_detail(city_response, city))
            elif len(store_list) > 0:
                for store in store_list:
                    store = url + store[2:]
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
