import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'http://myirving.com'


def validate(item):
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
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
    url = "http://myirving.com/ajaxpro/StationWebsites.SharedContent.Web.Common.Controls.Map.StoreData,StationWebsites.ashx"
    session = requests.Session()
    headers = {
        'Content-Type': 'text/plain; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-AjaxPro-Method': 'GetStorePins'
    }
    payload = {
        'pinType' : "1",
        'srl' : {
            'MaxLat' : "46.62103851470599",
            'MaxLong' : "-63.85878892319772",
            'MinLat' : "38.46421757364014",
            'MinLong' : "-79.01992307680223",
            'ZoomLevel' : "6"
        }
    }
    request = session.post(url, headers=headers, data=json.dumps(payload))
    store_list = json.loads(request.text)['value']['Payload']
    for store in store_list:
        output = []
        phone = get_value(store['PrimaryPhoneNumber'])
        store = store['Store']
        output.append(base_url) # url
        output.append(get_value(store['DisplayName'])) #location name
        output.append(get_value(store['Address'])) #address
        output.append(get_value(store['City'])) #city
        output.append(get_value(store['State'])) #state
        output.append(get_value(store['Zip'])) #zipcode
        output.append(get_value(store['Country'])) #country code
        output.append(get_value(store['ID'])) #store_number
        output.append(phone) #phone
        output.append('Irving Oil - Store Locator') #location type
        output.append(get_value(store['Latitude'])) #latitude
        output.append(get_value(store['Longitude'])) #longitude
        output.append('<MISSING>') #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
