import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://locations.churchs.com/"
    location_url = 'https://locations.churchs.com/api/5a6ba1f67735c821781c7dea/locations-details'
    r = requests.get(location_url,headers = header).json()
    addresses = []

    for val in r['features']:
        locator_domain = base_url

        location_name = val['properties']['name']
        street_address = val['properties']['addressLine1'] + ' ' + val['properties']['addressLine2']
        city = val['properties']['city']
        state = val['properties']['province']
        zip = val['properties']['postalCode']
        store_number = '<MISSING>'
        country_code = 'US'
        phone = val['properties']['phoneNumber']
        location_type = '<MISSING>'
        if len(val['geometry']['coordinates']) == 1:
            
            latitude = val['geometry']['coordinates'][0]
            
            longitude = val['geometry']['coordinates'][1]
        else:
            latitude = '<MISSING>'
            longitude = '<MISSING>'


        

        if(len(val['properties']['hoursOfOperation']['Sun']) == 1):
            sunday  = ' '.join(val['properties']['hoursOfOperation']['Sun'][0])
        else:
            sunday = "<MISSING>"

        

        hours_of_operation = 'Mon '+' '.join(val['properties']['hoursOfOperation']['Mon'][0]) + ' Tue '+' '.join(val['properties']['hoursOfOperation']['Tue'][0]) + ' Wed '+' '.join(val['properties']['hoursOfOperation']['Wed'][0]) + ' Thu '+' '.join(val['properties']['hoursOfOperation']['Thu'][0]) + ' Fri '+' '.join(val['properties']['hoursOfOperation']['Fri'][0]) + ' Sat '+' '.join(val['properties']['hoursOfOperation']['Sat'][0]) + ' Sun :'+sunday
        page_url = location_url

        if street_address in addresses:
            continue
        addresses.append(street_address)
        store=[]
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        
        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        store.append(page_url  if page_url else '<MISSING>')

        # print("====", str(store))
        return_main_object.append(store)
    return return_main_object

    
   


def scrape():
    data = fetch_data()  
    
    write_output(data)

scrape()
        
