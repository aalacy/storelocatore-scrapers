import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.americasmattress.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('&amp; ', '').strip()

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
    url = "https://www.americasmattress.com/gadsden/locations/finderajax"
    headers = {
        'Accept': '*/*',
        'Cookie': 'advanced-frontend=9lvbhj4n6dsoh9sb7b4kv1dos1; _csrf-frontend=3c251295262bcded4357b84ba5637f66146dbd801be75fe02ff22478c8d17beea%3A2%3A%7Bi%3A0%3Bs%3A14%3A%22_csrf-frontend%22%3Bi%3A1%3Bs%3A32%3A%22lEyt4ng610y60LT1L1vrMAgvjNfPiJur%22%3B%7D; _ga=GA1.2.137209347.1567798996; _gid=GA1.2.2109961790.1567798996; _gcl_au=1.1.2087005087.1567798998; _svsid=ee358b9d991c31b4b333aa9885d51684; _hjid=a71a08ac-f186-4e44-86f6-352e7f1d90d8; _fbp=fb.1.1567798998290.1733061126; visitor_id308121=44811587; visitor_id308121-hash=7a74ab4476b196b2ec6c030488fbc76631668c093699098ac7cef067a933539c153747542bb214863bc9e89867b1bfb59709b81b; calltrk_referrer=https%3A//www.americasmattress.com/national/locations/all; calltrk_landing=https%3A//www.americasmattress.com/gadsden; current_store=8f56b7590376a7796841c6dec9ec0540fa4871aee01abf00a376e9d002021d5aa%3A2%3A%7Bi%3A0%3Bs%3A13%3A%22current_store%22%3Bi%3A1%3Bi%3A79%3B%7D',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
        'X-CSRF-Token': 'XUUOu1gxqN-1sX53qa45jTeKre6-h3Jb2eB11MINgPUxAHfPbF_P6YSBB0GZ4m28e7vbnPPGFS2zrhOEq0f1hw==',
        'X-Requested-With': 'XMLHttpRequest'
    }
    session = requests.Session()
    source = session.get(url, headers=headers).text
    store_list = json.loads(source)
    for store in store_list:        
        output = []
        output.append(base_url) # url
        output.append(get_value(store['name'])) #location name
        output.append(get_value(store['address'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        output.append(get_value(store['zipcode'])) #zipcode
        output.append('US') #country code
        output.append(get_value(store['id'])) #store_number
        output.append(get_value(store['phone'])) #phone
        output.append("America's Mattress") #location type
        output.append(get_value(store['latitude'])) #latitude
        output.append(get_value(store['longtitude'])) #longitude
        if store['hours']:
            h_temp = []
            store_hours = json.loads(store['hours'])
            for key, hour in list(store_hours.items()):
                try:
                    if 'open' in hour and hour['open'] is not None and hour['open'] != '':
                        temp = key + ' ' + hour['open'] 
                    if 'close' in hour and hour['close'] is not None and hour['close'] != '':
                        temp += '-' + hour['close']
                    h_temp.append(temp)
                except Exception as e:
                    pdb.set_trace()
            store_hours = ', '.join(h_temp)
        else:
            store_hours = "<MISSING>"
        output.append(store_hours) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
