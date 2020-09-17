import csv
import re
from lxml import etree
import json
import usaddress
from sgrequests import SgRequests

base_url = 'https://revelatorcoffee.com/pages/locations'

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
    session = SgRequests()
    output_list = []
    url = "https://revelatorcoffee.com/pages/locations"
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//a[contains(@href, "https://revelatorcoffee.com/pages")]/@href')
    for store_link in store_list:
        store = etree.HTML(session.get(store_link).text)
        st_list = store.xpath('.//div[@class="rte grid__item"]//table//tr')
        for st in st_list:
            output = []
            detail = st.xpath('.//td')[1].xpath('.//p')
            output.append(base_url) # url
            output.append(validate(detail[0].xpath('.//text()')).split(':')[-1]) #location name
            address = validate(detail[1].xpath('.//text()'))
            address = parse_address(address)
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append('<MISSING>') #phone
            output.append("Revelator Coffee") #location type
            geo_loc = validate(st.xpath('.//a/@href'))
            lat = ''
            lng = ''
            if geo_loc != '':
                geo_loc = geo_loc.split('/@')
                if len(geo_loc) > 1:
                    geo_loc = geo_loc[1].split(',17')[0].split(',')
                    lat = geo_loc[0]
                    lng = geo_loc[1]                
            output.append(get_value(lat)) #latitude
            output.append(get_value(lng)) #longitude
            output.append(validate(detail[2].xpath('.//text()'))) #opening hours
            output_list.append(output)            

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
