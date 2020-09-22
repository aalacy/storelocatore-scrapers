import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.macaronigrill.com'

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
    url = "https://www.macaronigrill.com/locations/all-locations"
    session = requests.Session()
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[contains(@class, "location-result-cell")]')    
    for store in store_list:
        store_link = base_url + validate(store.xpath('.//a[@class="linkbutton"]/@href')[0])
        output = []
        page = session.get(store_link).text
        store = etree.HTML(page)
        details = eliminate_space(store.xpath('.//div[contains(@class, "location-content-block")]')[0].xpath('.//text()'))
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(get_value(store.xpath('.//div[contains(@class, "location-title")]//h2//text()'))) #location name       
        address = parse_address(', '.join(details[1:3]))
        output.append(address['street']) #address
        output.append(address['city']) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(details[3])) #phone
        output.append("Romano's Macaroni Grill Italian Restaurant") #location type
        geo_loc = eliminate_space(validate(store.xpath('.//div[contains(@class, "location-title")]//a/@href')[-1]).split(','))
        output.append(geo_loc[-2]) #latitude
        output.append(geo_loc[-1]) #longitude
        hours = json.loads(validate(page.split('var hours = ')[1].split('];')[0]) + ']')
        store_hours = []
        for hour in hours:
            store_hours.append(validate(hour['Day']) + ' ' + validate(hour['Open']) + ' - ' + validate(hour['Close']))
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
