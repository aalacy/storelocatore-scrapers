import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('unicobank_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
            

   

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://unicobank.com/"
    loacation_url = base_url+'/locations/'
    r = session.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"html.parser")
    ck = soup.find('div',{'class':'fusion-no-small-visibility'}).find_all('div',{'class':'fusion-column-wrapper'})
   
    for target_list in ck:
       
        if target_list.find('h2',{'class':'title-heading-center'}) != None:
                location_name = target_list.find('h2',{'class':'title-heading-center'}).text.strip()
                
                main_arry = target_list.find_all('div',{'class':'fusion-clearfix'})
                addr = main_arry[1].find_all('p')[0].text.strip().split('\n')
                
                # latitude = "<MISSING>"
                # longitude = "<MISSING>"
                # if main_arry[1].find_all('p')[0].find('a') != None:                
                latitude =  target_list.find_all('a')[0]['href'].split('@')[1].split(',')[0]
                
                longitude =  target_list.find_all('a')[0]['href'].split('@')[1].split(',')[1]                
                                
                if  len(addr) == 3:
                        
                        locator_domain = base_url
                        street_address = addr[0].strip()
                        city = addr[1].split(',')[0].strip()
                        state =  addr[1].split(',')[1].strip().split(' ')[0].strip()
                
                        zip = addr[1].split(',')[1].strip().split(' ')[1].strip()
                        kb = main_arry[1].find_all('p')[1].text.strip().replace('Phone:','')
                        phone = kb.replace('Tel:','').split('\n')[0].strip().replace('Tel. ','')

                if len(addr) == 4:

                        locator_domain = base_url
                        street_address = addr[0] + addr[1].strip()
                        
                        city = addr[2].split(',')[0].strip()
                        state =  addr[2].split(',')[1].strip().split(' ')[0].strip()
                
                        zip = addr[2].split(',')[1].strip().split(' ')[1].strip()
                        kb = main_arry[1].find_all('p')[1].text.strip().replace('Phone:','')
                        phone = kb.replace('Tel:','').split('\n')[0].strip().replace('Tel. ','')

                
                country_code = 'US'
                store_number = '<MISSING>'
                location_type = ''
                hours_of_operation = ' '.join(main_arry[0].text.strip().split('\n')).strip().replace("xa",'')
                page_url = '<MISSING>'
        
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
                store.append(page_url  if page_url else '<MISSING>')
                logger.info("data=====",store);
                yield store
                
def scrape():
    data = fetch_data()    
    write_output(data)

scrape()
