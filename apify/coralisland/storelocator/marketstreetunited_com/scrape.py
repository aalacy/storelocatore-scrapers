import csv
import re
import pdb
from lxml import etree
import json
import usaddress
from sgrequests import SgRequests

base_url = 'https://www.marketstreetunited.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip().replace('\n', '')

def get_value(item):
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
    url = 'https://www.marketstreetunited.com/RS.Relationshop/StoreLocation/GetAllStoresPosition' 
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "www.marketstreetunited.com",
        "Referer": "https://www.marketstreetunited.com/rs/StoreLocator",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }
    session = SgRequests()
    store_list = session.get(url, headers=headers).json()
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(validate(store["StoreName"])) #location name
        output.append(validate(store["Address1"])) #address
        output.append(validate(store["City"])) #city
        output.append(validate(store["State"])) #state
        output.append(validate(store["Zipcode"])) #zipcode
        output.append('US') #country code
        output.append(store["StoreID"]) #store_number
        output.append(validate(store["PhoneNumber"])) #phone
        output.append("Market Street in US") #location type
        output.append(validate(str(store["Latitude"]))) #latitude
        output.append(validate(str(store["Longitude"]))) #longitude
        output.append(get_value(store["StoreHours"])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
