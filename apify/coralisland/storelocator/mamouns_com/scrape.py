import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://mamouns.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '' or item == 'N/A':
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
    url = "https://mamouns.com/locations"
    session = requests.Session()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    source = request.text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="info"]')    
    data_list = json.loads(validate(source.split('>window.locationData = ')[1].split('</script>')[0]))
    for idx, store in enumerate(store_list):
        data = data_list[idx]        
        store = eliminate_space(store.xpath('.//div[@class="copy"]//text()'))
        output = []
        output.append(base_url) # url
        output.append(data['name']) #location name
        output.append(store[0]) #address
        address = store[1].replace(',', '').strip().split(' ')
        output.append(validate(address[:-2])) #city
        output.append(address[-2]) #state
        output.append(address[-1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store[-1])) #phone
        output.append("Mamoun's") #location type
        output.append(data['latitude']) #latitude
        output.append(data['longitude']) #longitude
        output.append(get_value(store[2:-1])) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
