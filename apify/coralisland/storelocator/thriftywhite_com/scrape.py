import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.thriftywhite.com'

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
    url = "https://www.thriftywhite.com/Store_Locations.cfm"
    page_url = ''
    session = requests.Session()
    source = session.get(url).text    
    store_list = source.split('var point = new GLatLng(')
    for store in store_list[1:]:
        more_info = etree.HTML('<table'+store.split('"<table')[1].split('table>"')[0]+'table>')
        sections = more_info.xpath('.//table[@class="mapText"]')
        details = eliminate_space(sections[0].xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(get_value(more_info.xpath('.//a[@class="mapLink"]/@href'))) # page url
        output.append(details[0]) #location name
        address = ''
        phone = ''
        for idx, de in enumerate(details):
            if 'phone' in de.lower():
                phone = de.replace('Phone:', '')
                address = ', '.join(details[1:idx])
        address = parse_address(address)
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode  
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(phone)) #phone
        output.append("Thrifty White Pharmacy") #location type
        geo_loc = store.split(');')[0].split(',')
        output.append(geo_loc[0]) #latitude
        output.append(geo_loc[1]) #longitude
        store_hours = []
        pharmacy_hours = []
        if len(sections) > 1:
            titles = eliminate_space(sections[1].xpath('.//td[@class="mapTitle"]//text()'))
            if len(titles) == 1:
                store_hours = eliminate_space(sections[1].xpath('.//text()'))
            else:
                hours = sections[1].xpath('.//tr')
                for hour in hours:
                    tds = hour.xpath('.//td')
                    if len(tds) > 0:
                        store_hours.append(validate(tds[0].xpath('.//text()')))
                        pharmacy_hours.append(validate(tds[-1].xpath('.//text()')))
        output.append(get_value(store_hours) + ' ' + validate(pharmacy_hours)) #opening hours
        output_list.append(output)                  
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
