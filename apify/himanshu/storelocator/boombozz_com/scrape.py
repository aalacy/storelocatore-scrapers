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
    base_url = "https://boombozz.com/"
    loacation_url = 'https://boombozz.com/wp-admin/admin-ajax.php?action=store_search&lat=38.23184&lng=-85.71014&max_results=25&search_radius=50&autoload=1'
    r = requests.get(loacation_url,headers = header).json()
    for idx, val in enumerate(r):  
           
               
        locator_domain = base_url            
        location_name = val['store']
        
        phone = val['phone']
       
        
        street_address = val['address']
        city = val['city']              
        state = val['state']
        zip = val['zip']
        j = soup = BeautifulSoup(val['hours'],"lxml")
        x = j.find_all('tr')
        bb = []
        for v in x:
            bb.append(v.find_all('td')[0].text +'-'+v.find_all('td')[1].text)
            

        hours_of_operation = ''.join(bb)
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = 'boombozz'
        latitude =  val['lat']
        longitude =  val['lng']

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
