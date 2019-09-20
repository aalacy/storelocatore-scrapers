import csv
import sys

import requests
from bs4 import BeautifulSoup
import re
import time
import json

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
        zips = sgzip.for_radius(100)

        # print(sgzip.coords_for_radius(50))
        addresses = []
        return_main_object = []
        header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
        base_url = 'https://www.chopard.com/'

        con = []

        get_data_url = 'https://www.chopard.com/intl/storelocator'

        r = requests.get(get_data_url, headers=header)

        soup = BeautifulSoup(r.text, "lxml")
        jk = json.loads(soup.find('select', {'class': 'country-field'}).find_previous('script').text.replace(
            'var preloadedStoreList =', '').replace(';', '').strip())



        for vj in jk['stores']:
            try:

                locator_domain = base_url

                location_name = vj['name'].encode('ascii', 'ignore').decode('ascii').strip()
                street_address = vj['address_1'].encode('ascii', 'ignore').decode('ascii').strip()

                city = vj['city'].encode('ascii', 'ignore').decode('ascii').strip()
                state = ''
                zip = ''
                if 'zipcode' in vj:
                    if vj['zipcode'] != None:
                        zip =  vj['zipcode'].encode('ascii', 'ignore').decode('ascii').strip()


                store_number = vj['store_code'].encode('ascii', 'ignore').decode('ascii').strip()
                country_code = vj['country_id'].encode('ascii', 'ignore').decode('ascii').strip()
                phone = vj['phone'].encode('ascii', 'ignore').decode('ascii').strip().replace(' /-','')
                location_type = 'chopard'
                latitude = vj['lat'].encode('ascii', 'ignore').decode('ascii').strip()
                longitude = vj['lng'].encode('ascii', 'ignore').decode('ascii').strip()

                if street_address in addresses:
                    continue
                addresses.append(street_address)
                r = requests.get(vj['details_url']
                                 , headers=header)
                soup = BeautifulSoup(r.text, "lxml")
                if len(soup.find_all('div',{'class':'data-block'})) == 2:
                    hours_of_operation = soup.find_all('div',{'class':'data-block'})[1].text.replace('Opening hours:','').encode('ascii', 'ignore').decode('ascii').strip()
                else:
                    hours_of_operation = ''

                store = []
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

                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                

                return_main_object.append(store)

            except:
                continue


        return  return_main_object


def scrape():
    data = fetch_data()
    write_output(data)
scrape()