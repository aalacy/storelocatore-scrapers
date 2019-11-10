import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.ritters.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").replace('\t', '').replace('\n', '').replace('  ', '').strip()

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
    url = "https://www.ritters.com/locations.php"
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'X-Mapping-geklhdma=33C5B3423D751E9600263F31D095B950; X-Mapping-dminehmk=31BA39BB7DDDA405494F2B8793667659',
        'Host': 'www.ritters.com',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
    }
    source = session.get(url, headers=headers, verify=False).text
    data = validate(source.split('values:[')[1])
    store_list = eliminate_space(data.split(',],options')[0].split('{latLng:['))    
    for store in store_list:        
        store_id = validate(store.split('location.php?id=')[1].split('>')[0]).replace("'", "")
        store_link = 'https://www.ritters.com/location.php?id=' + store_id
        geo_loc = eliminate_space(store.split(']')[0].split(','))
        store_info = etree.HTML(session.get(store_link,  headers=headers).text)
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        is_comming = validate(store_info.xpath('.//div[contains(@class, "coming-soon-label ")]//text()'))
        if is_comming != '':
            continue
        output.append(get_value(store_info.xpath('.//h2//span//text()'))) #location name
        details = eliminate_space(store_info.xpath('.//div[@class="location-info-text"]//text()'))
        output.append(details[1]) #address
        address = details[2].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append(store_id) #store_number
        phone = ''
        store_hours = ''
        for de in details:
            if 'Phone:' in de:
                phone = validate(de.replace('Phone:', ''))
            if 'from'  in de:
                store_hours = validate(de)
        output.append(get_value(phone)) #phone
        output.append("Ritter's Frozen Custard") #location type
        output.append(get_value(geo_loc[0])) #latitude
        output.append(get_value(geo_loc[1])) #longitude
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
