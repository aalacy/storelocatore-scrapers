import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.northitaliarestaurant.com'

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
    url = "https://www.northitaliarestaurant.com/locations/"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="location-view-details listing-button"]//a/@href')
    for link in store_list:
        data = validate(etree.HTML(session.get(link).text).xpath('.//script[@type="application/ld+json"]//text()'))
        store = json.loads(data)
        output = []
        output.append(base_url) # url
        output.append(get_value(store['name']) + ' in ' + get_value(store['address']['addressLocality'])) #location name
        output.append(get_value(store['address']['streetAddress'])) #address
        output.append(get_value(store['address']['addressLocality'])) #city
        output.append(get_value(store['address']['addressRegion'])) #state
        output.append(get_value(store['address']['postalCode'])) #zipcode
        output.append(get_value(store['address']['addressCountry'])) #country code
        output.append('<MISSING>') #store_number
        phone = ''
        if 'telephone' in store:
            phone = store['telephone'].replace('+', '')
        output.append(get_value(phone)) #phone
        output.append('Handmade Pasta | Handmade Pizza | North Italia') #location type
        output.append(get_value(store['geo']['latitude'])) #latitude
        output.append(get_value(store['geo']['longitude'])) #longitude
        store_hours = []
        if 'openingHoursSpecification' in store:
            for hour in store['openingHoursSpecification']:
                store_hours.append(validate(hour['dayOfWeek']).split('/')[-1] + ' ' + validate(hour['opens']) + '-' + validate(hour['closes']))
            output.append(get_value(store_hours)) #opening hours        
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
