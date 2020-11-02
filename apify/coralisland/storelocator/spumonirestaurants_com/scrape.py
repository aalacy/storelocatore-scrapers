import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'http://www.spumonirestaurants.com'


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
    url = "http://www.spumonirestaurants.com/wp-admin/admin-ajax.php?action=store_search&lat=34.019454&lng=-118.49119100000001&max_results=25&search_radius=50"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(store['store']) #location name
        output.append(get_value(store['address'] + ' ' + store['address2'])) #address
        output.append(store['city']) #city
        output.append(store['state']) #state
        output.append(store['zip']) #zipcode
        output.append(store['country']) #country code
        output.append(store['id']) #store_number
        output.append('<MISSING>') #phone
        output.append("Spumoni - Trattoria & Pizzeria") #location type
        output.append(store['lat']) #latitude
        output.append(store['lng']) #longitude
        h_temp = []
        if store['hours']:
            store_hours = etree.HTML(store['hours']).xpath('.//tr')
            for hour in store_hours:
                hour = validate(hour.xpath('.//text()'))
                h_temp.append(hour)
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
