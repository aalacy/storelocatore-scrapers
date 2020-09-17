import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://freedomfitness.com'

def eliminate_space(items):
    tmp = []
    for item in items:
        item = item.strip()
        if item != '':
            tmp.append(item)
    return tmp

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://freedomfitness.com/wp-admin/admin-ajax.php?action=store_search&lat=27.80058&lng=-97.39638&max_results=25&search_radius=50&autoload=1"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append( store['store'].split('&#8211;')[0] if '&#8211;' in store['store'] else store['store']) #location name
        output.append(store['address'] + ' ' + store['address2']) #address
        output.append(store['city']) #city
        output.append(store['state']) #state
        output.append(store['zip']) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(store['phone'] if store['phone'] != 'N/A' else '<MISSING>') #phone
        output.append('Gyms') #location type
        output.append(store['lat']) #latitude
        output.append(store['lng']) #longitude
        link = base_url + store['url']
        h_temp = '<MISSING>'
        if link:
            data = etree.HTML(session.get(link).text)
            h_temp = ' '.join(eliminate_space(data.xpath('.//div[@class="club_hours_inner"]')[0].xpath('.//text()')))
        output.append(h_temp) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
