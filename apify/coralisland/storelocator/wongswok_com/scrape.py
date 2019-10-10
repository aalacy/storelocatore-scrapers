import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://wongswok.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").strip()

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
    url = "https://monica-durant-7jpl.squarespace.com/locations"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'cookie': 'crumb=BUdyD4F88akgMjYxZDdmZTkzYWQzMjFlZWM2OWQ2ZWE4YjEwZTUy; ss_cvr=64cdc92b-c7aa-420e-833d-9b1dcea59b29|1568417634205|1568417634205|1568664467337|2; ss_cvt=1568664467337',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    source = session.get(url, headers=headers).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="col sqs-col-4 span-4"]')
    count = len(store_list)/3
    for idx in range(0, count):
        idx = idx * 3
        details = eliminate_space(store_list[idx].xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append('<MISSING>') #location name
        output.append(details[0]) #address
        address = details[1].strip().split(',')
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(details[2]) #phone
        output.append("Wong's Wok") #location type
        geo_loc = json.loads(validate(store_list[idx+1].xpath('.//div[@class="sqs-block map-block sqs-block-map sized vsize-6"]/@data-block-json')))
        output.append(validate(geo_loc['location']['mapLat'])) #latitude
        output.append(validate(geo_loc['location']['mapLng'])) #longitude
        output.append(get_value(details[4:-1])) #opening hours
        output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
