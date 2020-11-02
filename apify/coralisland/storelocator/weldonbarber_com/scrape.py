import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://weldonbarber.com'


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

def check(item, arr):
    for a in arr:
        if item.lower() in a.lower():
            return True
    return False

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    history = []
    output_list = []
    url = "https://weldonbarber.com/locations/"
    session = requests.Session()
    request = session.get(url)
    source = etree.HTML(request.text)
    data = validate(source.xpath('//script[@type="application/ld+json"]//text()')[1])
    missing_stores = source.xpath('//div[contains(@class, "wpb-column wpb-col-4")]')
    store_list = json.loads(data)['@graph']
    for store in store_list[2:]:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['name']).split('-')[1]) #location name
        output.append(get_value(store['address']['streetAddress'])) #address
        output.append(get_value(store['address']['addressLocality'])) #city
        output.append(get_value(store['address']['addressRegion'])) #state
        output.append(get_value(store['address']['postalCode'])) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['telephone']).replace('+', '')) #phone
        output.append('Weldon Barber') #location type
        output.append(get_value(store['geo']['latitude'])) #latitude
        output.append(get_value(store['geo']['longitude'])) #longitude
        store_hours = []
        if store['openingHoursSpecification']:
            for hour in store['openingHoursSpecification']:
                if type(hour['dayOfWeek']) == list:
                    for day in hour['dayOfWeek']:
                        store_hours.append(day + ' ' + hour['opens']+'-'+hour['closes'])
                else:
                    store_hours.append(hour['dayOfWeek'] + ' ' + hour['opens']+'-'+hour['closes'])
        output.append(get_value(store_hours)) #opening hours
        history.append(store['address']['streetAddress'])
        output_list.append(output)
    for mstore in missing_stores:
        detail = eliminate_space(mstore.xpath('.//text()'))
        output = []
        output.append(base_url) # url
        if len(detail) > 1 and check(detail[1], history) == False:
            output.append(detail[0]) #location name
            output.append(detail[1]) #address
            address = detail[2].strip().split(',')
            output.append(address[0]) #city
            output.append(address[1].strip().split(' ')[0]) #state
            output.append(address[1].strip().split(' ')[1]) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(detail[3]) #phone
            output.append('Weldon Barber') #location type
            geo_loc = mstore.xpath('.//a/@href')[0].split('ll=')
            if len(geo_loc) > 1:
                geo_loc = geo_loc[1].split('&')[0].split(',')
            else:
                geo_loc = session.get(mstore.xpath('.//a/@href')[1]).text.split('!1d')[1].split('"')[0].split('!2d')
            output.append(geo_loc[0]) #latitude
            output.append(geo_loc[1]) #longitude
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
