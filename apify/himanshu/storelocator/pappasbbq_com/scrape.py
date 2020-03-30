import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import re


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
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','accept':'*/*'}
    return_main_object = []
    base_url = "https://pappasbbq.com/"
    loacation_url = base_url+'locations/xml_all.php'
    r = session.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    for val in soup.find_all("marker"):
        

        locator_domain = base_url
        location_name = val['name'].strip()

        street_address = val['street'].strip().replace('Terminal','').replace('  C Gate 14','')
        city = val['city'].split(',')[0].strip()
        state = val['city'].split(',')[1].strip().split(' ')[0].strip()
            
        if len(val['city'].split(',')[1].strip().split(' ')) == 2:
            zip = val['city'].split(',')[1].strip().split(' ')[1].strip()
        
        store_number = '<MISSING>'
        country_code = 'US'
        phone = val['phone'].strip()
        location_type = 'pappasbbq'
        latitude = val['lat'].strip()
        longitude = val['lng'].strip()
        hours_of_operation =  BeautifulSoup(val['hoursstatus'],"lxml")
        ck = hours_of_operation.find('div',{'class':'profile_hours_all'}).find_all('div',{'class':'hours_group'})
        dk = []
        for vv in ck:
            dk.append(vv.text+'-')
            
        hours_of_operation = ' '.join(dk).replace('Dining Room:',' ')

        
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
