import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.jugojuice.com'

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.jugojuice.com/en/locations/list"
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Cookie': 'locale=en; request_method=POST; _jugojuice_session=bUxLNGptK1dJS2V2emdrUnlYSDBSanRRQnQ4dS9jekVSTmRibG94bTlaSUVjcVZQaTN6UW5JV1NLOUE4YWo0Z2ZTZ1NFMVk4anRKM2lSWUxGQnAzWDl2dnkrREFtZTQ1WGZHN2ZPRTdQNW1HUWZyMFB5d2ZMdU5vd0Y1Z2RQN2VZUEtrQXJlaWxyRVpwWVh1aEt0dzVnPT0tLWlxZWpXczIyRXlzcm9ZSmQ1Rml3OFE9PQ%3D%3D--525a5d4769f0a9a97523b441701cf9247cbbae15',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    city_list = etree.HTML(session.get(url, headers=headers).text).xpath('.//select[@id="city"]//option/@value')
    for city in city_list:
        formdata = {        
            'authenticity_token': '7M11xrowR56or3+1rRi2cb1ogcUmBeVRl/xJi61vsSM66J7RKMfp8Zu+oExjITXKeXoA8TKuVMHXgtDzS3c9EA==',
            'city': str(city)
        }
        source = session.post(url, data=formdata, headers=headers).text
        response = etree.HTML(source)
        store_list = response.xpath('//div[@class="list-view"]//article[@class="location"]')
        for store in store_list:
            output = []
            output.append(base_url) # url
            output.append(validate(store.xpath('.//h3[@itemprop="name"]//text()'))) #location name
            output.append(validate(store.xpath('.//span[@itemprop="streetAddress"]//text()'))) #address        
            output.append(validate(store.xpath('.//span[@itemprop="addressLocality"]//text()'))) #city
            output.append(validate(store.xpath('.//span[@itemprop="addressRegion"]//text()')[0])) #state
            output.append(validate(store.xpath('.//span[@itemprop="addressRegion"]//text()')[1])) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(validate(store.xpath('.//span[@itemprop="telephone"]//text()'))) #phone
            output.append("Jugo Juice") #location type
            geo_loc = validate(store.xpath('.//img/@src')).split('center=')[1].split('&')[0].split(',')
            output.append(get_value(geo_loc[0])) #latitude
            output.append(get_value(geo_loc[1])) #longitude
            store_hours = validate(eliminate_space(store.xpath('.//div[@class="hours"]//text()'))).replace('Hours', '')
            output.append(get_value(store_hours)) #opening hours
            output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
