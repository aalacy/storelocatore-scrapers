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
    base_url = "https://mandarinrestaurant.com/"
    loacation_url = base_url+'locations/'
    r = requests.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    v = soup.find('div',{'id':'wpsl-stores'}).find_all('ul')
    for target_list in v:
        
        fetch_li   = target_list.find_all('li')
        
        for dk in fetch_li:
            
            locator_domain = base_url
            fetch_p = dk.find_all('p')
            fetch_p.pop(0)
            
            location_name = fetch_p[0].find('a').text
            street_address = fetch_p[1].find('span').text

            phone = fetch_p[3].find('span').text.split(':')[1]
            db = fetch_p[2].find('span').text.split(' ')
             
            zip = db[-2]+db[-1]            
            state = db[-3]
            db.pop(-1)
            db.pop(-1)
            db.pop(-1)
            city = ' '.join(db)
            vv = fetch_p[2].find('span').text.split(' ')
            
            if not db:
                 
                 zip = vv[-1]            
                 state = vv[-2]
                 city = vv[-3]

            
            country_code = 'CANADA'
            store_number = dk['data-store-id']
            location_type = 'mandarinrestaurant'
            latitude =  '<MISSING>'
            longitude =  '<MISSING>'
            hours_of_operation =  '<MISSING>'
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

