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
    base_url = "https://mnbbank.com/"
    loacation_url = base_url+'locations/'
    r = requests.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    vk = soup.find('div',{'class':'int-content'}).find_all('div',{'class':'loc-container'})
    
    for target_list in vk:

        for x in  target_list.find_all('div',{'class':'loc-left'}):



            locator_domain = base_url
            location_name = target_list.find('h3').text.strip()

            cb = x.find('h4').text.replace('\xa0','').strip().split('\n')

            if len(cb) == 1:
                kb = cb[0].strip().split(',')
                street_address = kb[0].strip()
                city = '<MISSING>'
                state = kb[1].strip().split(' ')[0].strip()
                zip =  kb[1].strip().split(' ')[1].strip()
            else:

                street_address = cb[0].strip()
                city = cb[1].split(',')[0].strip()
                state = cb[1].split(',')[1].strip().split(' ')[0].strip()
                zip = cb[1].split(',')[1].strip().split(' ')[1].strip()

            country_code = 'USA'
            location_type = 'mnbbank'
            store_number = '<MISSING>'
            if x.find('h5') != None:
                phone = x.find('h5').text.replace('Phone: ','').strip()
            else:
                phone = '<MISSING>'

            latitude = '<MISSING>'
            longitude = '<MISSING>'

            hours_of_operation = target_list.find('div',{'class':'loc'}).find_all('p')
            fk = []
            for gg in hours_of_operation:
                fk.append(gg.text.replace('ATM Available',''))

            hours_of_operation = ' '.join(list(fk)).strip().replace('\n','').replace('\r','')

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
       

def scrape():
    data = fetch_data()    
    write_output(data)

scrape()
