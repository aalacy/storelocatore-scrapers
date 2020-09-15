import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.lunchboxwax.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip().replace('\n', '').replace('\t', '')

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
    url = "https://www.lunchboxwax.com/salons/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="main-wide"]//li[@class="item"]')
    for store in store_list:        
        link = get_value(store.xpath('.//strong[@class="name"]//a/@href'))
        link = base_url + link
        detail = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        output.append(get_value(detail.xpath('.//div[@class="title-box"]//h4//text()'))) #location name
        output.append(validate(eliminate_space(store.xpath('.//span[@class="address"]//text()'))[:-1])) #address
        output.append(get_value(store.xpath('./@data-city'))) #city
        output.append(get_value(store.xpath('./@data-state')).upper()) #state
        output.append(get_value(store.xpath('./@data-zip'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//strong[@class="number"]//text()'))) #phone
        output.append("LunchboxWax | Waxing Salon | Waxing Services") #location type
        output.append(get_value(store.xpath('./@data-latitude'))) #latitude
        output.append(get_value(store.xpath('./@data-longitude'))) #longitude
        output.append(validate(eliminate_space(detail.xpath('.//ul[@id="LocalMapAreaOpenHour"]//text()')))) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
