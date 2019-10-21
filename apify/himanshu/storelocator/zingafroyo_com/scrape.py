import csv
import requests
from bs4 import BeautifulSoup

import re

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
    base_url = "http://zingafroyo.com/"
    loacation_url = base_url
    r = requests.get(loacation_url,headers = header)
    soup = BeautifulSoup(r.text,"html.parser")

    vk  = soup.find('div',{'id':'pu469'}).find_all('img')
    for target_list in vk:
        jk  = target_list['alt'].split('ZINGA')
        jk.pop(0)
        # print(jk)
        # print('~~~~~~~')
        for bn in jk:
            # print(bn)
            # print('~~~~~~~~~`')


            bn = bn.replace('\x80','')
            city = bn.strip().split(',')[0].strip().split(' ')
            if len(city) != 8:
                city = city[-1]
            else:
                city = " ".join(city[-2:])


            street_address = bn.strip().split(',')[0].strip()
            locator_domain = base_url


            state =bn.strip().split(',')[1].strip().split()[0].replace('.','').strip()
            zip = bn.strip().split(',')[1].strip().split()[1].replace('âª','').strip()
            location_name = city+","+state

            if len(bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')) == 3:

                hours_of_operation = bn.strip().split(',')[1].strip().split('Store Hours:')[1].strip().replace('FLORIDA',' ')

                phone = bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')[2].strip()


            if len(bn.strip().split(',')[1].strip().split('Store Hours:')[0].strip().split(' ')) == 2:

                hours_of_operation = bn.strip().split(',')[1].strip().split('Store Hours:')[1].strip().replace('FLORIDA',' ')
                phone =''
            # print(hours_of_operation + " "+phone)






            country_code = "US"
            store_number = '<MISSING>'
            location_type = '<MISSING>'
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
            store.append(base_url)

            print(store)
            print('~~~~~~~~~~~~~')
            return_main_object.append(store)





    return return_main_object



    # return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
