import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('umd.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://locations.umb.com/"
    r = requests.get(base_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    href = soup.find_all('div',{'class':'map-list-item'})
    for target_list in href:
        href  = target_list.find('a')['href']
        
        vr = requests.get(href,headers = header)
        soup = BeautifulSoup(vr.text,"lxml")
        vk = soup.find('div',{'class':'col-maplist'}).find('div',{'class':'map-list-wrap'}).find('ul',{'class':'map-list'}).find_all('li',{'class':'map-list-item-wrap'})
        
        
        for target_list in vk:
            link = target_list.find('a',{'class':'ga-link'})['href']

            vr = requests.get(link,headers = header)
            soup = BeautifulSoup(vr.text,"lxml")

            locator_domain = 'https://www.umb.com/'
            location_name  = link.split('/')[-2]
            fb = soup.find('div',{'class':'address'}).find_all('div')
            street_address = ' '.join(list(fb[0].stripped_strings))
            temp = ' '.join(list(fb[1].stripped_strings)).split(',')
            city = temp[0]
           
            state = temp[1].strip().split(' ')[0]
            zip  = temp[1].strip().split(' ')[1]
            store_number = '<MISSING>'
            phone = soup.find('div',{'class':'map-list-links'}).find('a',{'class':'phone'}).text
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = 'umb'
            latitude = '<MISSING>'
            longitude = '<MISSING>'
            hours_of_operation = ' '.join(list(soup.find_all('script')[7].stripped_strings)).split(';')[1].split('=')[1]
           
           
            db = json.loads(hours_of_operation)
            gk = []
            for idx, val in enumerate(db['days']):
                
               
                if type(db['days'][val]) is str:

                    gk.append(val+':'+db['days'][val])
                    
                elif type(db['days'][val]) is list:
                   for x in db['days'][val]:
                       gk.append(val+': Open: '+x['open']+' Close: '+x['close'])

            hours_of_operation = ' '.join(gk)
            
            
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
