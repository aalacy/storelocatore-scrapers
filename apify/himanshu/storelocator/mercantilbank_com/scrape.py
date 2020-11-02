import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mercantilbank_com')





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
    base_url = "https://www.amerantbank.com/"
    location_url  = 'https://www.amerantbank.com/wp-admin/admin-ajax.php?action=locations_archive_get_map_locations&data=post-type%3Dlocations%26posts-per-page%3D-1'
    r = session.get(location_url ,headers = header).json()

    bb  = 'https://www.amerantbank.com/wp-admin/admin-ajax.php?action=load_posts&data=post-type%3Dlocations%26posts-per-page%3D-1'
    lol = session.get(bb ,headers = header).json()
    
    soup = BeautifulSoup(lol['html'],"lxml")
    for idx, val in enumerate(r['locations']): 
        
        if soup.find('div',{'id':val['id']}).find('div',{'class':'text-primary'}) != None:
            hours_of_operation = soup.find('div',{'id':val['id']}).find('div',{'class':'text-primary'}).find_previous('div').text.strip()
        
        
        if len(val['address']) > 0:
            
            locator_domain = base_url
            location_name = val['name'].strip()
            if len(val['address'].replace('<br />','').split('\n')) == 2:
                street_address = val['address'].replace('<br />','').split('\n')[0].strip()
                city = val['address'].replace('<br />','').split('\n')[1].split(',')[0].strip()
                
                if len(val['address'].replace('<br />','').split('\n')[1].split(',')[1].strip().split(' '))  == 3:
                    state = val['address'].replace('<br />','').split('\n')[1].split(',')[1].strip().split(' ')[0] + ' ' +val['address'].replace('<br />','').split('\n')[1].split(',')[1].strip().split(' ')[1]
                    zip = val['address'].replace('<br />','').split('\n')[1].split(',')[1].strip().split(' ')[2]
                    logger.info(state)
                    logger.info(zip)
                else:
                    state = val['address'].replace('<br />','').split('\n')[1].split(',')[1].strip().split(' ')[0]                
                    zip = val['address'].replace('<br />','').split('\n')[1].split(',')[1].strip().split(' ')[1]
                   
            if len(val['address'].replace('<br />','').split('\n')) == 3:

                street_address = val['address'].replace('<br />','').split('\n')[0].strip() + val['address'].replace('<br />','').split('\n')[1].strip()
                city = val['address'].replace('<br />','').split('\n')[2].strip().split(',')[0]
                state = val['address'].replace('<br />','').split('\n')[2].strip().split(',')[1].strip().split(' ')[0]
                zip = val['address'].replace('<br />','').split('\n')[2].strip().split(',')[1].strip().split(' ')[1]
                
            
    
            store_number = '<MISSING>'
            country_code = 'US'
            phone = val['phone'].strip()
            location_type = 'amerantbank'
            latitude = val['lat'].strip().replace(',','')
            longitude = val['lng'].strip().replace(',','')
            
            
            
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
            logger.info(store)
    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)

scrape()
