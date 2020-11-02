import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.searsoptical.com'

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
            if len(row) > 0:
                writer.writerow(row)

def parse_detail(store, link):
    try:
        output = []
        output.append(base_url) # url
        output.append(link) # url
        output.append(get_value(store.xpath('.//div[@class="Hero-fullName"]//text()')))#location name
        output.append(get_value(validate(store.xpath('.//div[@class="Core-mainRow l-row"]//span[@class="c-address-street-1"]//text()')) + ' ' + validate(store.xpath('.//div[@class="Core-mainRow l-row"]//span[@class="c-address-street-2"]//text()')))) #address
        output.append(get_value(store.xpath('.//div[@class="Core-mainRow l-row"]//span[@class="c-address-city"]//text()'))) #city
        output.append(get_value(store.xpath('.//div[@class="Core-mainRow l-row"]//abbr[@class="c-address-state"]//text()'))) #state
        output.append(get_value(store.xpath('.//div[@class="Core-mainRow l-row"]//span[@class="c-address-postal-code"]//text()'))) #zipcode
        output.append(get_value(store.xpath('.//div[@class="Core-mainRow l-row"]//abbr[contains(@class, "c-address-country-name")]//text()'))) #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store.xpath('.//div[@id="phone-main"]//span[@class="Core-phoneText"]//text()'))) #phone
        output.append("Auto Insurance Quotes - Car Insurance ") #location type
        geo = validate(store.xpath('.//img[@itemprop="map"]/@data-src')).split('center=')[1].split('&channel')[0].split('%2C')
        output.append(geo[0]) #latitude
        output.append(geo[1]) #longitude
        output.append(get_value(eliminate_space(store.xpath('.//table[@class="c-hours-details"]//tbody//text()')))) #opening hours
        # if 'Coming Soon' not in output[1] and 'Closed' not in output[1]:        
        return output
        # else:
        #     return []
    except Exception as e:
        pdb.set_trace()

def fetch_data():
    output_list = []
    url = "https://agents.allstate.com/"
    locator_url = 'https://agents.allstate.com/'
    session = requests.Session()
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "cookie": "__cfduid=d1850c63207344d154294aa2f859529bb1567802901; ak_bmsc=1F850CC39AE1E17970B4DE400B9382DCADDE9437F05E000027D58F5DDD8D2721~plR6xiGEzj3eLtjOigHp5eiKIjuJL5GqAvv0RTRMXVdzgiMK2Dc43mltk+zgKVf5iB0KkMDhcCkVMG03V6wXcLq8K44A2lnTwjYqhgTYyXqsaJlGF6NlB/IBtD03s0VqOHUQCzgSRqF7vohZNe1LZahgdrgyRvtj4sJWLcHFUmUeo9hfCm2ZiFSNp30sjyu61sa5n2k+p+SwfUp+JiOpdiRYEKQ9666FZAkx1XFo1O50k=; s_invisit=1; s_vnum=4; s_cc=true; s_ppv=-; s_dl=1; s_cmgvo=typed%2Fbookmarkedtyped%2Fbookmarkedundefined; s_v58=%5B%5B'typed%2Fbookmarked'%2C'1569707316357'%5D%5D; bm_mi=3D07B7F4104FE248B2A117BAF6A56949~7yG1Ua/ugRwvzHhF+qrwoKg0ax87axoe/jzgPOEhQ//oUlA7XFwqrtEyRhnekvKXBT8pUq0QCf5bG4SPS2t7IdpvSQBFQlBif/+1o0AzXwzhv226yNN5A3NIRa52hhS1dDD1lIJfbGrLAYwwPT2C5mBtrBoTzgOM9kQCTLuaVtrUAfnmJGoFn1ufOSSuz/aMdCsC936XKz2tKlqEzym1lwlp/VjpZk3IGys7mzHDQGWb/e3eZ9cAIbZsgBha3c+2yfKZNeE5s50R2znfSu/B1UeqHiphGGf1Zbq88vwiuowWseGLD1/tOyVBUckQkWbP; bm_sv=F8A8A3E91AD5E4DE4CC144F0B35BD217~AG5qlrJdy4qhS7K9H2oAJWxxMgofiP0fgtJraImQO7vZhJrUGPj6OCShXZ9QFL7tHY7YbA0+J8KUOohOKzD4Q6j/XA69WN9uwM+rhxIokUgOc44DaPDuBZxCcJh4rLaqS6t6rPPVTtlSKWycrXWX4Qun9oWlSkFPDAe26g1WHKg=; s_dslv=1569707374270; s_gpp=so%3Afeature%3Afind%20a%20location; utag_main=_st:1569709174199$ses_id:1569707792076%3Bexp-session$prevpage:; s_sq=luxsearsopticalprod%3D%2526pid%253Dso%25253Afeature%25253Afind%252520a%252520location%2526pidt%253D1%2526oid%253Dhttps%25253A%25252F%25252Flocations.searsoptical.com%25252F%2526ot%253DA",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    state_list = response.xpath('//a[@class="Directory-listLink"]/@href')
    for state in state_list:
        if 'http' not in state:
            state = locator_url + state.replace('../', '')
        state_response = etree.HTML(session.get(state, headers=headers).text)
        city_list = state_response.xpath('//a[@class="Directory-listLink"]/@href')
        store_list = state_response.xpath('//a[@class="Teaser-upper l-row"]/@href')
        if len(city_list) > 0:
            for city in city_list:
                if 'http' not in city:
                    city = locator_url + city.replace('../', '')
                city_response = etree.HTML(session.get(city, headers=headers).text)
                store_list = city_response.xpath('//a[@class="Teaser-upper l-row"]/@href')
                if len(store_list) > 0:
                    for store in store_list:
                        if 'http' not in store:
                            store = locator_url + store.replace('../', '')
                        store_response = etree.HTML(session.get(store, headers=headers).text)
                        output_list.append(parse_detail(store_response, store))
                else:
                    output_list.append(parse_detail(city_response, city))
        elif len(store_list) > 0:
            for store in store_list:
                if 'http' not in store:
                    store = locator_url + store.replace('../', '')
                store_response = etree.HTML(session.get(store, headers=headers).text)                
                output_list.append(parse_detail(store_response, store))
        else:
            output_list.append(parse_detail(state_response, state))
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

