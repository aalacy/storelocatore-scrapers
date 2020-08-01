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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://salonlofts.com/"


    r = session.get(base_url+'salons/',headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    v  = soup.find('select',{'id':'market_id'}).find_all('option')
   
   
    for idx, val in enumerate(v):
        if idx > 0:
            # print(+val['value'])
            r = session.get("https://salonlofts.com"+val['value'],headers = header)
            soup = BeautifulSoup(r.text,"lxml")
            vk = soup.find('ul',{'class':'stores'}).find_all('div',{'class':'store'})
            
            for key, value in enumerate(vk):

                locator_domain = base_url
                page_url = value['data-store-uri'].strip()
                location_name = value['data-store-name'].strip()
                street_address = value['data-store-address'].strip()
                city = value['data-store-city'].strip()
                state = value['data-store-state'].strip()
                zip = value['data-store-zip'].strip()
                country_code = 'US'
                location_type = '<MISSING>'
                store_number = value['data-store-id'].strip()
                phone = '<MISSING>'
                latitude = value['data-store-latitude'].strip()
                longitude =  value['data-store-longitude'].strip()
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
                store.append("https://salonlofts.com"+page_url  if page_url else '<MISSING>')


                return_main_object.append(store)  
    return return_main_object        

        
def scrape():
    data = fetch_data()  
    
    write_output(data)

scrape()
