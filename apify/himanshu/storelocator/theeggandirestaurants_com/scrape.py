import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
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
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://theeggandirestaurants.com/"
    loacation_url = base_url+'wp-admin/admin-ajax.php?action=crb_location'
    r = session.get(loacation_url,headers = header).json()
    
    for idx, val in enumerate(r['locations']):
        latitude = val['lat'].strip()
        longitude = val['lng'].strip()
        r = session.get(val['url'],headers = header)
        soup = BeautifulSoup(r.text,"lxml")
        locator_domain = base_url
        location_name = soup.find('div',{'class':'contact-box'}).find('div',{'class':'entry'}).find('h1').text.strip()
        
        vk = soup.find('ul',{'class':'contact-address'}).find_all('li')
        street_address = vk[0].find('span').text.split('\n')[0].strip()
        city = vk[0].find('span').text.split('\n')[1].split(',')[0].strip()
        state = vk[0].find('span').text.split('\n')[1].split(',')[1].strip().split(' ')[0].strip()

        zip = vk[0].find('span').text.split('\n')[1].split(',')[1].strip().split(' ')[1].strip()
        store_number = '<MISSING>'
        phone = vk[1].find('span').text.strip()
        
        country_code = 'US'
        location_type = 'theeggandirestaurants'
        vc =  vk[2].find('span').text.split('\n')               
        
        if len(vc)  == 3:
            vc.pop(-1)
            
            hours_of_operation = vc[0]+vc[1].strip()
        elif len(vc)  == 2:
            vc.pop(-1)
            
            hours_of_operation = ''.join(vc).replace('Open Daily:','').strip()
        
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
