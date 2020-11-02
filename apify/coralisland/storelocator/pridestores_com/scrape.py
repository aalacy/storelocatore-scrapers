import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://pridestores.com'


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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://pridestores.com/__locations.php"
    session = requests.Session()
    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'exp_last_visit=1253737271; exp_csrf_token=4a338d53ebeeebda82525d052b4bc031e18704bf; exp_tracker=%7B%220%22%3A%22locations%22%2C%221%22%3A%22index%22%2C%22token%22%3A%226c259e0536808b985936ba535c989dd5a61d5b854f910cb9ae234ab4b989f6d89d27ab1a54a33347e6f97149d96ea05a%22%7D; exp_last_activity=1569097291',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    formdata = {
        'cat': '',
        'count': '0',
        'zipcitystate':''
    }
    request = session.post(url, headers=headers, data=formdata)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['title'])) #location name
        link = 'https://pridestores.com/locations/store-details/'+validate(store['url_title'])
        # address = ', '.join(eliminate_space(details.xpath('.//div[@class="direction-left"]//p//text()')))
        phone = ''
        address = []
        details = eliminate_space(etree.HTML(store['field_id_31']).xpath('.//text()'))
        for idx, de in enumerate(details):
            if 'phone' in de.lower():
                phone = validate(re.findall("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}", validate(details[idx:])))
                address = details[:idx]
        if len(address) == 0:
            address = details
        address = parse_address(', '.join(address))
        if 'close' not in address['street'].lower():
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
            output.append('US') #country code
            output.append('<MISSING>') #store_number
            more_info = etree.HTML(session.get(link).text)
            more_details = eliminate_space(more_info.xpath('.//div[@class="store-left"]//p//text()'))
            store_hours = []
            for more_idx, more_de in enumerate(more_details):
                if 'pride' in more_de.lower():
                    phone = validate(re.findall("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}", validate(more_details[more_idx:]))[0])
                    store_hours = more_details[:more_idx]
            if len(store_hours) == 0:
                store_hours = more_details
            output.append(get_value(phone)) #phone
            output.append('Pride Stores') #location type
            output.append(get_value(store['field_id_57'])) #latitude
            output.append(get_value(store['field_id_56'])) #longitude
            if 'subway' in validate(store_hours).lower():
                store_hours = validate(store_hours).lower().split('subway')[0]
            output.append(get_value(store_hours)) #opening hours            
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
