import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://parkerskitchen.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

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
    url = "https://parkerskitchen.com/wp-content/themes/parkers/get-locations.php?origAddress=8120+US-280%2C+Ellabell%2C+GA+31308%2C+USA"
    session = requests.Session()
    request = session.get(url)    
    store_list = json.loads(request.text)
    for store in store_list:
        phone = ''
        hours = ''
        store_name = get_value(store['name']).replace('&#8217;', "'")        
        details = eliminate_space(etree.HTML(session.get(validate(store['web'])).text).xpath('.//div[@id="locations-text"]//text()'))
        for idx, de in enumerate(details):
            if 'phone' in de.lower():
                phone = validate(de.split('Phone:')[1])
            if 'hour' in de.lower():
                hours = details[idx+1:]
                break
        store_hours = validate(hours)
        for h_idx, hour in enumerate(hours):
            if 'kitchen' in hour.lower() or 'drive' in hour.lower():                
                store_hours = validate(hours[:h_idx])
                break
        if 'kitchen' in store_hours.lower():
            pdb.set_trace()
        output = []
        output.append(base_url) # url
        output.append(store_name) #location name
        output.append(get_value(store['address'] + ' ' + store['address2'])) #address        
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        output.append(get_value(store['postal'])) #zipcode
        output.append('US') #country code
        output.append(store_name.split('#')[-1]) #store_number
        output.append(get_value(phone)) #phone
        output.append("Southwest GA Oil S'S food stores") #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['lng'])) #longitude
        output.append(get_value(store_hours)) #opening hours     
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
