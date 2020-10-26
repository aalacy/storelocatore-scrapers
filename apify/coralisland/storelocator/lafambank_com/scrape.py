import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json
import usaddress

base_url = 'https://www.lafambank.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('AMP;', '').strip()

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'content-length': '48',
        'path': '/api/Branches/Search',
        'scheme': 'https',
        'method': 'POST',
        'authority': 'www.fultonbank.com',
        'referer': 'https://www.fultonbank.com/Maps-and-Locations',
        'origin': 'https://www.fultonbank.com',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'x-requested-with': 'XMLHttpRequest',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'upgrade-insecure-requests': '1',
    }
    
    data = { 'QueryModel.SearchTerm': '17601', 'QueryModel.Radius': 30 }
    url = 'https://www.fultonbank.com/api/Branches/Search'
    stores_json = session.post(url, headers=headers, data=data).json()
    details = etree.HTML(stores_json['branchFlyouts']).xpath('//div[@data-id]')
    stores = etree.HTML(stores_json['branchResults']).xpath('//div[@data-id]')
    print(len(stores))
    for (store, detail) in zip(stores, details):
        lat = store.attrib['data-lat']
        lng = store.attrib['data-long']
        name = store.attrib['data-name'].strip()
        if 'atm only' in name.lower():
            continue
        store_number = store.attrib['data-id']
        raw_address = store.xpath('.//span[@class="location-address"]')[0].text
        address = parse_address(raw_address)
        street = address['street']
        city = address['city']
        state = address['state']
        zipcode = address['zipcode']
        locator_domain = 'fultonbank.com'
        phone = detail.xpath('.//a[contains(@href, "tel")]')[0].attrib['href'].split(':')[1].strip()
        raw_hours = detail.xpath('.//span[contains(@class, "hours-extended")]')[0]
        hours_of_operation = ', '.join([x.strip() for x in raw_hours.itertext() if x.strip()])
        country_code = 'US'
        page_url = '<MISSING>'
        location_type = '<MISSING>'
        yield [locator_domain, name, street, city, state, zipcode, country_code, store_number, phone, location_type, lat, lng, hours_of_operation, page_url]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
