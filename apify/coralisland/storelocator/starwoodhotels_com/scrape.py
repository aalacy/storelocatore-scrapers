import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://st-regis.marriott.com'

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
    url = "https://st-regis.marriott.com/hotel-directory/"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    source = validate(request.text.split('window.MARRIOTT_DIRECTORY_DATA = ')[1].split('</script>')[0])[:-1]
    store_list = json.loads(source)['properties']
    for key, store in list(store_list.items()):        
        output = []
        if store['country'] == 'CA' or store['country'] == 'US':
            output.append(base_url) # url
            output.append(store['name']) #location name
            output.append(store['address']) #address
            output.append(validate(eliminate_space(store['city'].replace('us', '').replace('on_ca', 'on').replace('_', ' ').split(' '))[:-1]).capitalize()) #city
            output.append(store['state']) #state
            output.append(store['zipcode']) #zipcode
            output.append(store['country']) #country code
            output.append("<MISSING>") #store_number
            output.append(store['phone']) #phone
            output.append("Experience 5-star Luxury | St. Regis Hotels & Resorts") #location type
            output.append(store['latitude']) #latitude
            output.append(store['longitude']) #longitude
            output.append("<MISSING>") #opening hours            
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
