import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.jimsrestaurants.com/"
    location_url  = 'https://www.jimsrestaurants.com/locations/locations/json'
    r = session.get(location_url ,headers = header).json()
    for idx, val in enumerate(r):
       
        locator_domain = base_url
        location_name = val['name']
        vc = BeautifulSoup(val['address'],"lxml")
       
        street_address = vc.find('span',{'class':'address-line1'}).text.strip()
        city = vc.find('span',{'class':'locality'}).text.strip()
        state = vc.find('span',{'class':'administrative-area'}).text.strip()
        zip = vc.find('span',{'class':'postal-code'}).text.strip()
        store_number = '<MISSING>'
        country_code = 'US'
        phone = val['field_phone']
        location_type = 'jimsrestaurants'
        vb = val['field_location_coordinates']
       
        gg = str(vb).replace('[{"coordinates":["','')
        vn = gg.replace('"]}]','')
        

        latitude = vn.split(',')[0].replace('"','')
        
        longitude = vn.split(',')[1].replace('"','')
        hours_of_operation = val['field_hours']

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
        

        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)

scrape()
