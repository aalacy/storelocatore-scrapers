import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.agentprovocateur.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip().replace('\r\n', ',')

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
            state = addr[0].replace(',', '') + ' '
        else:
            street += addr[0].replace(',', '') + ' '
    if get_value(state) == 'York':
        state = 'NY'
        city = 'New york'
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.agentprovocateur.com/gb_en/storelocator/location/getstores"
    page_url = 'https://www.agentprovocateur.com/gb_en/storelocator'
    session = requests.Session()
    headers = {
        'Accept': 'text/javascript, text/html, application/xml, text/xml, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'X-NewRelic-ID': 'VQcFV1FVARAJXFNQDgcG',
        'X-Requested-With': 'XMLHttpRequest',
    }

    formdata = {
        'city': '',
        'list': '1'
    }
    request = session.post(url, headers=headers, data=formdata)
    markers = json.loads(request.text)['markers']
    store_list = json.loads(markers)
    for store in store_list:        
        country_code = get_value(store['country_code'])
        if country_code == 'US':
            output = []
            output.append(base_url) # url
            output.append(page_url) # page url
            output.append(get_value(store['title'])) #location name
            address = validate(store['address_display']).replace('USA', '')
            address = parse_address(address)
            output.append(address['street']) #address
            if address['city'] == '<MISSING>':
                output.append(get_value(store['city'])) #city
            else:
                output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode
            output.append(country_code) #country code
            output.append(get_value(store['location_id'])) #store_number
            output.append(get_value(store['phone']).replace('+', '')) #phone
            output.append('Luxury Lingerie Worldwide') #location type
            output.append(get_value(store['latitude'])) #latitude
            output.append(get_value(store['longitude'])) #longitude
            store_hours = 'Weekday ' + get_value(store['opening_hours_weekday']) + ', '
            store_hours += 'Saturday ' + get_value(store['opening_hours_saturday']) + ', '
            store_hours += 'Sunday ' + get_value(store['opening_hours_sunday'])
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
