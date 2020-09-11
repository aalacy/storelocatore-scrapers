import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.hyatt.com/brands/andaz'


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
    url = "https://www.hyatt.com/explore-hotels/map/filter?brands=Andaz"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        if get_value(store['address']['region']) == 'North America':
            page_url = get_value(store['info']['propertySiteUrl'])
            details = json.loads(validate(etree.HTML(session.get(page_url).text).xpath('//script[@type="application/ld+json"]//text()')))
            output.append(base_url) # url
            output.append(page_url) # page url
            output.append(get_value(details['name'])) #location name
            output.append(get_value(details['address']['streetAddress'])) #address
            output.append(get_value(details['address']['addressLocality'])) #city
            output.append(get_value(details['address']['addressRegion'])) #state
            output.append(get_value(details['address']['postalCode'])) #zipcode
            output.append(get_value(details['address']['addressCountry'])) #country code
            output.append('<MISSING>') #store_number
            output.append(get_value(details['telephone'])) #phone
            output.append('Luxury Boutique Hotels | Andaz Hotels By Hyatt') #location type
            output.append(get_value(store['location']['latitude'])) #latitude
            output.append(get_value(store['location']['longitude'])) #longitude
            store_hours = []
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
