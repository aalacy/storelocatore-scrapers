import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://kiwifrozenyogurt.com'

def validate(item):    
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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://kiwifrozenyogurt.com/locations/"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="our-locations__block--left-img clearfix"]//a/@href')
    extra_url = 'https://kiwifrozenyogurt.com/wp-admin/admin-ajax.php'
    extra_response = session.post(extra_url, 
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',            
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        },
        data={
            'action': 'zi_load_location_ajaxcall',
            'display_post': '4',
            'current_paged': '1'
        }).text
    extra = eliminate_space(etree.HTML(extra_response).xpath('.//a/@href'))[0]
    store_list.append(extra)
    for link in store_list:
        data = etree.HTML(session.get(link).text)
        store = data.xpath('.//div[@class="locations-details-left clearfix"]')[0]
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h1//text()'))) #location name
        address = eliminate_space(store.xpath('.//h2//text()'))
        output.append(validate(address[:-2])) #address        
        output.append(address[-2]) #city
        output.append(address[-1]) #state
        output.append("<MISSING>") #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//a//text()'))) #phone
        output.append("Kiwi Frozen Yogurt") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(validate(eliminate_space(store.xpath('.//li//text()')))) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
