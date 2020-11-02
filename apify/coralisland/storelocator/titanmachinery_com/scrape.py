import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://titanmachinery.com'


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
    url = "https://titanmachinery.com/api/default/locations?$orderby=MapName&&$format=application/json;odata.metadata=none&$expand=LocationImage"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)['value']
    for store in store_list:        
        output = []
        if get_value(store['LocationAddress']['CountryCode']) == 'US':
            output.append(base_url) # url
            output.append(validate(store['LocationName'])) #location name
            output.append(get_value(store['LocationAddress']['Street'])) #address
            output.append(get_value(store['LocationAddress']['City'])) #city
            output.append(get_value(store['LocationAddress']['StateCode'])) #state
            output.append(get_value(store['LocationAddress']['Zip'])) #zipcode
            output.append(get_value(store['LocationAddress']['CountryCode'])) #country code
            output.append(get_value(store['LocationId'])) #store_number
            output.append(get_value(store['LocationPhonePrimary'])) #phone
            output.append("Titan Machinery") #location type
            output.append(get_value(str(store['LocationAddress']['Latitude']))) #latitude
            output.append(get_value(str(store['LocationAddress']['Longitude']))) #longitude
            days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            store_hours = []
            for day in days_of_week:
                week = 'LocationSummerHours' + day
                val = store[week]
                if val == '':
                    val = 'Closed'
                store_hours.append(day + ' ' + val)
            output.append(', '.join(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
