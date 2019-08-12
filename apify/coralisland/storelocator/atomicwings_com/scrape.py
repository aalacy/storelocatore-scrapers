import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.prestigepreschoolacademy.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

def get_value(item):
    item = validate(item)
    if item == '' or item == 'N/A':
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
    url = "https://api.responsival.net/atomicwings/locations.php"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(store['name']) #location name
        address = usaddress.parse(store['address'])
        street = ''
        city = ''
        state = ''
        zipcode = ''
        for addr in address:
            if addr[1] == 'PlaceName':
                city += addr[0].replace(',', '') + ' '
            elif addr[1] == 'ZipCode':
                zipcode = addr[0]
            elif addr[1] == 'StateName':
                state = addr[0]
            else:
                street += addr[0].replace(',', '') + ' '
        output.append(get_value(street)) #address
        output.append(get_value(city)) #city
        output.append(get_value(state)) #state
        output.append(get_value(zipcode)) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['phone'])) #phone
        output.append("Atomic Wings") #location type
        output.append(store['latitude']) #latitude
        output.append(store['longitude']) #longitude
        store_hours = '  '
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days_of_week:
            store_hours += day.capitalize() + ' ' + store[day+'-hours'] + ', '
        output.append(get_value(store_hours[:-2])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
