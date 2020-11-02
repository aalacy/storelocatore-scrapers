import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.ampm.com'


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
    url = "https://www.ampm.com/handlers/getlocation.ashx?loc=90025&sl=true&ns=10000&rd=5000"
    session = requests.Session()
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'cookie': 'ASP.NET_SessionId=1dbo5dgayoqi1gpk3p4tu20v; cookienotice=yes; userZip=90025',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append('<MISSING>') #location name
        output.append(get_value(store['address'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        output.append(get_value(store['zipcode'])) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['phone'])) #phone
        output.append('ampm Store') #location type
        output.append(get_value(store['latitude'])) #latitude
        output.append(get_value(store['longitude'])) #longitude
        output.append('<MISSING>') #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
