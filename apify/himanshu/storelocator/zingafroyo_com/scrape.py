import csv
import requests
from bs4 import BeautifulSoup

import re

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
    base_url = "http://zingafroyo.com/"
    loacation_url = base_url
    r = requests.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"html.parser")

    vk  = soup.find('div',{'id':'pu469'}).find_all('img')
    for target_list in vk:
        jk  = target_list['alt'].split('ZINGA')
        jk.pop(0)
        for bn in jk:

            bn = bn.replace('\x80','')         
            city = bn.strip().split(',')[0].strip().split(' ')[-1]
            street_address = bn.strip().split(',')[0].strip()
            locator_domain = base_url
            location_name = bn.strip().strip().split(' ')[0]

            # print(len(bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')))
            
            
            if len(bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')) == 3:
                state = bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')[0].strip()
                zip = bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')[1].strip().replace('âª','')
                hours_of_operation = bn.strip().split(',')[1].strip().split('Store Hours:')[1].strip().replace('FLORIDA',' ')

                phone = bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')[2].strip()


            if len(bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')) == 2:
                state = bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')[0].strip()
                zip = bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')[1].strip().replace('âª','')
                hours_of_operation = bn.strip().split(',')[1].strip().split('Store Hours:')[1].strip().replace('FLORIDA',' ')
                phone =''


            if city == "City":
                city = bn.strip().split(',')[0].strip().split(' ')[-2]

            if state == "Virginia":
                state = 'VA'

            country_code = "US"
            store_number = '<MISSING>'
            location_type = 'zingafroyo' 
            latitude = '<MISSING>'
            longitude = '<MISSING>'
            

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
            
            # print(store)
            return_main_object.append(store)  

           
            
        

    return return_main_object          
    
   
   
    # return return_main_object            
              
def scrape():
    data = fetch_data()    
    write_output(data)

scrape()
