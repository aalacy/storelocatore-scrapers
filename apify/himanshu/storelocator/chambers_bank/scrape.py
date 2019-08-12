import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
    base_url = "https://www.chambers.bank/"
    r = requests.get(base_url+'locations/',headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    db =  soup.find_all('div',{'class':'location'})
   
    for val in db:
        
        locator_domain = base_url
        
        

        location_name = val.find_previous('h3').text
       
        street_address = val.find('p',{'class':'address'}).text.split('\n')[0].strip()
       
        
        city =  val.find('p',{'class':'address'}).text.split('\n')[1].strip().split(',')[0].strip()
        
        state = val.find('p',{'class':'address'}).text.split('\n')[1].strip().split(',')[1].strip().split(' ')[0].strip()
        zip = '<MISSING>'
        store_number = '<MISSING>'

        phone = val.find('p',{'class':'address'}).find_next('p').text.replace('Phone:','').strip()
       
        
        
        country_code = 'US'        
        location_type = 'chambers'
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        hours_of_operation = val.find_all('div',{'class':'hours-row'})
        bn = []
        for target_list in hours_of_operation:
            bn.append(target_list.text.strip())
        hours_of_operation = ''.join(bn)

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
