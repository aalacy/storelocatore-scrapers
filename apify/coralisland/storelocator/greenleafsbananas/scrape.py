import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.greenleafsbananas.com'

def validate(item):
    item = ''.join(item).replace('\xa0', '').replace('\u2019', '').strip()
    if item == '':
        item = '<MISSING>'
    return item

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://app.mapply.net/front-end//get_surrounding_stores.php?api_key=mapply.6ef6000b0df2780d9cfac8e36e38aaad&latitude=34.0522342&longitude=-118.2436849&max_distance=0&limit=100&calc_distance=1"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)['stores']
    for store in store_list:
        try:
            output = []
            detail = etree.HTML(store['detailed'])
            output.append(base_url) # url
            output.append(validate(detail.xpath('//span[@class="name"]//text()'))) #location name
            output.append(validate(detail.xpath('//span[@class="address"]//text()'))) #address
            city = validate(detail.xpath('//span[@class="city"]//text()'))
            output.append(city) #city
            output.append(validate(detail.xpath('//span[@class="prov_state"]//text()'))) #state
            output.append(validate(detail.xpath('//span[@class="postal_zip"]//text()'))) #zipcode
            country_code = 'US'
            if 'cairo' in city.lower():
                country_code = 'EG'
            if 'dubi' in city.lower():
                country_code = 'IN'
            output.append(country_code) #country code
            output.append(store['store_id']) #store_number
            phone = validate(detail.xpath('//span[@class="phone"]//text()'))
            output.append(phone) #phone
            output.append('Bananas Restaurants') #location type
            output.append(store['lat']) #latitude
            output.append(store['lng']) #longitude        
            output.append('<MISSING>') #opening hours
            output_list.append(output)
        except Exception as e:
            pass
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
