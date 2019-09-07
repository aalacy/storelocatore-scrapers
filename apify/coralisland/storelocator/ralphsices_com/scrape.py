import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress

base_url = 'https://www.ralphsices.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").replace("&#39;", "'").replace("&amp;", '&').replace('&#44;', '').strip()

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
        'state' : get_value(state).replace('York', 'NY'), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.ralphsices.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1566558786121"
    session = requests.Session()
    headers = {
        'Accept': 'application/xml, text/xml, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    request = session.get(url, headers=headers)
    response = etree.HTML(request.text)
    store_list = response.xpath('.//store//item')
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//location//text()'))) #location name
        address = get_value(store.xpath('.//address//text()')).split('USA')[0].split('United States')[0]
        if 'New York' not in address:
            address = address.split('  ')[0]
        address = parse_address(address)
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode   
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//telephone//text()'))) #phone
        output.append("Ralph's Famous Italian Ices & Ice Cream | Long Island, New Jersey, Staten Island") #location type
        output.append(get_value(store.xpath('.//latitude//text()'))) #latitude
        output.append(get_value(store.xpath('.//longitude//text()'))) #longitude
        output.append("<MISSING>") #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
