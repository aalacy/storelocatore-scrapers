import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.wegmans.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "https://www.wegmans.com/stores.html"
    page_url = ''
    session = requests.Session()
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Cookie":'"wegmans-custom={"storeInfo":{"storeId":"LOCATION_25","name":"Pittsford","personalShopping":"no","zip":"14618","lat":"43.1061","long":"-077.5437"}}; AWSELB=13F9F9D91E084680D1110E0FA98E3F55836773F91887B0A14AB1E17DAB850A32F62F751432E6F98CFEBA0FAF1DB3D2CA791EC57BE238721FFA88D375CDE3508D0D1AE70502; __unam=abee5fe-16d78e39232-6764127d-20',
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
    }
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="column-control parbase section"]//a/@href')
    for store_link in store_list[8:]:
        if 'https:' not in store_link:
            store_link = base_url + store_link
        store = etree.HTML(session.get(store_link, headers=headers).text)
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        output.append(get_value(store.xpath('.//meta[@name="name"]/@content'))) #location name
        output.append(get_value(store.xpath('.//meta[@name="address"]/@content'))) #address
        output.append(get_value(store.xpath('.//meta[@name="city"]/@content'))) #city
        output.append(get_value(store.xpath('.//meta[@name="stateAbbreviation"]/@content'))) #state
        output.append(get_value(store.xpath('.//meta[@name="zip"]/@content'))) #zipcode  
        output.append('US') #country code
        output.append(get_value(store.xpath('.//meta[@name="locationNumber"]/@content'))) #store_number
        output.append(get_value(store.xpath('.//meta[@name="phone"]/@content'))) #phone
        output.append(get_value(store.xpath('.//meta[@name="locationType"]/@content'))) #location type
        geo_loc = validate(store.xpath('.//meta[@name="location"]/@content')).split('-0')
        output.append(geo_loc[0]) #latitude
        output.append('-'+geo_loc[1]) #longitude
        # store_hours = validate(store.xpath('.//meta[@name="description"]/@content')).split('Store Hours:')[-1]
        store_hours = validate(store.xpath('.//div[@class="address-info"]/div/text()'))
        # if store_hours != '':
        if 'Call' in store_hours:
            store_hours = store_hours.split('Call')[0]
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
