import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'http://pizzadepot.ca'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.encode('ascii', 'ignore').encode("utf8").replace("'", '').strip()

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
    url = "http://pizzadepot.ca/location/"
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Cookie': '_ga=GA1.2.1413556867.1566836552; _gcl_au=1.1.339031034.1566836552; PHPSESSID=08ca79e659004c9564e2646aaa912829; _gid=GA1.2.1156589308.1567451912; _gat=1; _gat_UA-99013361-1=1; gwcc=%7B%22fallback%22%3A%229056549711%22%2C%22clabel%22%3A%22zRXMCKn4iIMBELDB0ZYD%22%2C%22backoff%22%3A86400%2C%22backoff_expires%22%3A1567538311%7D',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    source = request.text
    data = validate(source.split('var depots = [];')[1].split('var map')[0])
    store_list = data.split('depots')
    for store in store_list[1:-2]:
        store = store.split('= [')[1].split('];')[0].split(', ')
        output = []
        output.append(base_url) # url
        output.append(get_value(store[0])) #location name
        output.append(get_value(store[1])) #address
        output.append(get_value(store[0])) #city
        output.append('<MISSING>') #state
        output.append(get_value(store[2])) #zipcode
        output.append('CA') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store[3])) #phone
        output.append("Pizza Depot - Best Pizza Store") #location type
        output.append(get_value(store[-3])) #latitude
        output.append(get_value(store[-2])) #longitude
        output.append(get_value(', '.join(eliminate_space(etree.HTML(store[-1]).xpath('.//text()'))))) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
