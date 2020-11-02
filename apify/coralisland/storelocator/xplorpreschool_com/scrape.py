import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'http://www.xplorpreschool.com'


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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "http://www.xplorpreschool.com/wp-admin/admin-ajax.php?action=nobel_schools&change=true&query=los+angeles&radius=5000&program=All&type=latlng&location%5Blat%5D=34.0522342&location%5Blng%5D=-118.2436849"
    page_url = ''
    session = requests.Session()
    headers = {
        'Accept': '*/*',
        'Cookie': 'PHPSESSID=788ef983baf79bcbdfc080d514c25d23',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)['data']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['url'])) # page url
        output.append(get_value(store['name'])) #location name
        output.append(get_value(store['address'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        output.append(get_value(store['zip'])) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(get_value(store['phone'])) #phone
        output.append('Private Preschools') #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['lng'])) #longitude
        output.append('<MISSING>') #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
