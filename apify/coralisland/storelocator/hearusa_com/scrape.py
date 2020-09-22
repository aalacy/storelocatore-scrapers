import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.hearusa.com'


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

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '')
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    history = []
    with open('cities.json') as data_file:    
        city_list = json.load(data_file)
    output_list = []
    session = requests.Session()
    for city in city_list:
        url = "https://www.hearusa.com/wp-admin/admin-ajax.php?action=store_search&lat="+str(city['latitude'])+"&lng="+str(city['longitude'])+"&max_results=100&search_radius=100"
        request = session.post(url)
        store_list = json.loads(validate(request.text))
        for store in store_list:
            output = []
            if store['id'] not in history:
                output.append(base_url) # url
                output.append(get_value(store['store'])) #location name
                output.append(get_value(store['address'] + store['address2'])) #address
                output.append(get_value(store['city'])) #city
                output.append(get_value(store['state'])) #state
                output.append(get_value(store['zip'])) #zipcode
                output.append('US') #country code
                output.append('<MISSING>') #store_number
                output.append(get_value(store['phone'])) #phone
                output.append("Super Store Finder") #location type
                output.append(get_value(store['lat'])) #latitude
                output.append(get_value(store['lng'])) #longitude
                store_hours = validate(eliminate_space(etree.HTML(session.get(store['permalink']).text).xpath('.//div[@class="centers__header__hours"]//text()'))).replace('Hours: ', '')
                output.append(store_hours) #opening hours
                output_list.append(output)
                history.append(store['id'])
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
