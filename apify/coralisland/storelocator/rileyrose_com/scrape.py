import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.rileyrose.com'


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
    url = "https://www.rileyrose.com/us/shop/Info/GetFindStoreList"
    session = requests.Session()
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'content-length': '57',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'x-newrelic-id': 'VQEDU19aABACV1RXDwcFU1E=',
        'x-requested-with': 'XMLHttpRequest'
    }
    body = {
        'latitude': '34.037627',
        'longitude': '-118.27282539999999',
        'keyword': ''
    }
    request = session.post(url, headers=headers, data=body)
    store_list = json.loads(request.text)['F21StoreList']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(store['Location']) #location name
        output.append(get_value(store['Address'] + ' ' + store['Address2'])) #address
        output.append(store['City']) #city
        output.append(store['State']) #state
        output.append(store['ZIP']) #zipcode
        output.append(store['CountryName']) #country code
        output.append(store['StoreID']) #store_number
        output.append(get_value(store['Phone'])) #phone
        output.append("Riley Rose") #location type
        output.append(store['Latitude']) #latitude
        output.append(store['Longitude']) #longitude
        store_hours = []
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Saturday', 'Friday', 'Sunday']
        for day in days_of_week:
            if store[day] != '':
                store_hours.append(day + ' ' + store[day])
        output.append(get_value(', '.join(store_hours))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
