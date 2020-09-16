import csv
import re
import pdb
from lxml import etree
import usaddress
from sgrequests import SgRequests
import re

base_url = 'https://www.brush32.com'

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
    url = "https://www.brush32.com/locations/"
    page_url = ''
    session = SgRequests()
    request = session.get(url)
    source = etree.HTML(request.text)
    stores = source.xpath('//section[@class="section-locations-grid"]//li[@class="locations-list-item"]')
    for store in stores:
        lat = store.attrib['data-lat']
        lng = store.attrib['data-lng']
        name = store.xpath('.//h3[@class="location-title"]/text()')[0]
        raw_address = [x.strip() for x in store.xpath('.//address[@class="location-address"]')[0].itertext() if x.strip()]
        street = raw_address[1]
        csz = raw_address[2].split()
        zipcode = csz[-1].strip()
        state = csz[-2].strip()
        city = raw_address[2].split(',')[0].strip()
        phone = store.xpath('.//a[@class="office-phone-swap"]/text()')[0].strip()
        page_url = store.xpath('(.//div[@class="location-links"]/a)[1]/@href')[0]
        locator_domain = 'brush32.com'
        location_type = '<MISSING>'
        hours = '<MISSING>'
        country = 'US'
        store_number = '<MISSING>'
        if 'brush32' in page_url:
            yield [locator_domain, page_url, name, street, city, state, zipcode, country, store_number, phone, location_type, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
