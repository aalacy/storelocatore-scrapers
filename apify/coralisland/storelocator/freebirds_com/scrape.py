import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://freebirds.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://freebirds.com/api/restaurants?includePrivate=false"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)['restaurants']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(store['name']) #location name
        output.append(store['streetaddress']) #address
        output.append(store['city']) #city
        output.append(store['state']) #state
        output.append(store['zip']) #zipcode
        output.append('US') #country code
        output.append(store['id']) #store_number
        output.append(store['telephone']) #phone
        output.append('<Missing>') #location type
        output.append(store['latitude']) #latitude
        output.append(store['longitude']) #longitude
        output.append('10:30 am-9:00 pm') #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
