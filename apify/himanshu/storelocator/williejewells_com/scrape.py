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
    base_url = "http://williejewells.com/"
    r = session.get(base_url+'order-online-locations/',headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    db =  soup.find_all('div',{'class':'location-tile'})
    for idx, val in enumerate(db):
        locator_domain = base_url
        location_name = val.find('h2').text
        street_address = val.find('address').text.split(',')[0]
        city = val.find('address').text.split(',')[1].strip()
        state = val.find('address').text.split(',')[2].strip().split(' ')[0]
        zip = val.find('address').text.split(',')[2].strip().split(' ')[1]
        store_number = '<MISSING>'
        if val.find('p').find('a') != None:
            phone = val.find('p').find('a').text.replace('Phone:','').strip()
        else:
            phone = '<MISSING>'
        country_code = 'USA'        
        location_type = 'williejewells'
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        hours_of_operation = '<MISSING>'
        
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
