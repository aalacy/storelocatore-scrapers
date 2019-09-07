import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://chuzefitness.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip().replace('&#038;', '')

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://chuzefitness.com/locations/"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    source = session.get(url, headers=headers).text
    data = source.split('var chuze_vars = ')[1].split('};')[0] + '}'
    store_list = json.loads(data)['all_markers']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(validate(etree.HTML(get_value(store['title'])).xpath('.//text()'))) #location name
        output.append(get_value(store['address_1'] + ' ' + store['address_2'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['state'])) #state
        output.append(get_value(store['zipcode'])) #zipcode
        output.append('US') #country code
        output.append(get_value(store['id'])) #store_number
        output.append(get_value(store['phone'])) #phone
        output.append('Chuze Fitness: Health Club & Fitness Center | Affordable Gym') #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['lng'])) #longitude
        store_hours = ''
        if 'url' in store:
            detail = etree.HTML(session.get(store['url'], headers=headers).text)
            store_hours = ', '.join(eliminate_space(detail.xpath('.//div[@class="open-hours info-item"]//text()')))
        output.append(get_value(store_hours)) #opening hours
        if 'coming' not in output[1].lower():
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
