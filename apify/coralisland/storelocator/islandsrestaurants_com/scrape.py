import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.islandsrestaurants.com'

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
        if item != '' or item != '\n':
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


def fetch_data():
    output_list = []
    history = []
    url = "https://www.islandsrestaurants.com/locations/search"
    with open('./cities.json') as data_file:    
        city_list = json.load(data_file)  
    session = requests.Session()
    headers={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'popup=true; geolocation=no; ll3=0.0%2C0.0; _islands_restaurant_website_session=lpt9sIj45Frb1lbRgj9jriFG0wt9%2BH7hFObp2s3PzHur3tT9pQnW8O5fE6d%2BgxOPY5T9Cz4Mm6ZWH6zxa4BmeRCwriqtvAhdPL%2FfZ6znjPlYnFXWSPnpfysTA%2F23Tm08%2BTLMWM%2FRPqHn8fGuZKg%3D--oCDmFY1AmhwxpQHq--Ab90qzBjN%2BI7idpTR2tNDw%3D%3D',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    }
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for city in city_list:
            formdata = {
                'authenticity_token': '5/a+ND4uRlbboXttxFoj290EjK1ZuUA06PQHG3jBjLE0JtJqZksfCaXr0IXZjXbl/zx0QPmqKvgBV2R2WhTCdQ==',
                'search': city['city'].lower() + ', ' + city['state'].lower()                
            }
            source = session.post(url, headers=headers, data=formdata).text
            response = etree.HTML(source)
            store_list = response.xpath('//div[@class="location-item"]')
            for store in store_list:
                output = []
                store_link = base_url + get_value(store.xpath('.//a/@href')[0])
                if store_link not in history:
                    history.append(store_link)
                    output.append(base_url) # url
                    output.append(store_link) # page url
                    output.append(get_value(store.xpath('.//h3//text()'))) #location name
                    output.append(get_value(store.xpath('.//div[@class="address"]//text()'))) #address
                    address = validate(store.xpath('.//div[@class="city-state-zip"]//text()')).replace(',', '').split('\n')        
                    output.append(address[0]) #city
                    output.append(address[1]) #state
                    output.append(address[2]) #zipcode
                    output.append('US') #country code
                    output.append("<MISSING>") #store_number
                    output.append(get_value(store.xpath('.//div[@class="phone"]//a/@href')).replace('tel:', '')) #phone
                    output.append("Islands Restaurant") #location type
                    output.append("<MISSING>") #latitude
                    output.append("<MISSING>") #longitude
                    output.append(get_value(eliminate_space(store.xpath('.//div[@class="hours"]//text()'))).replace('\n', '')) #opening hours
                    writer.writerow(output)

fetch_data()
