import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.chopard.com'

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
    url = "https://www.chopard.com/intl/storelocator"
    session = requests.Session()
    source = session.get(url).text
    data = json.loads(validate(source.split('var preloadedStoreList = ')[1].split('</script>')[0])[:-1])
    store_list = data['stores']
    for store in store_list:
        output = []
        if store['country_id'].lower() == 'ca'  or store['country_id'].lower() == 'us':
            output.append(base_url) # url
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address_1'])) #address
            if 'ontario' in get_value(store['city']).lower():
                city = get_value(store['city']).split(' ')
                output.append(city[0]) #city
                output.append(city[1]) #state
                output.append(validate(city[2:])) #zipcode                
            else:
                output.append(get_value(store['city'])) #city
                output.append('<MISSING>') #state
                output.append(get_value(store['zipcode'])) #zipcode
            output.append(get_value(store['country'])) #country code
            output.append(get_value(store['id'])) #store_number
            output.append(get_value(store['phone'])) #phone
            output.append('Chopard - Swiss Luxury Watches and Jewellery Manufacturer') #location type
            output.append(get_value(store['lat'])) #latitude
            output.append(get_value(store['lng'])) #longitude
            output.append('<MISSING>') #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
