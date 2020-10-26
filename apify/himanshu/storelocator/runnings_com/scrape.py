

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # driver = get_driver()

    return_main_object = []
    addresses = []
    result_coords = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.runnings.com/"
   


    location_url = "https://www.runnings.com/"

    r = session.get(location_url, headers=headers)
    # r_utf = r.text.encode('ascii', 'ignore').decode('ascii')
    soup = BeautifulSoup(r.text, "lxml")

    i = 0
    for x in soup.find('select',{'class':'runnings-store'}).find_all('option'):

        # data = 'id='+str(x['value'])
        location = session.get('https://www.runnings.com//storelocator/storedetails/post?id='+str(x['value'])).json()

        locator_domain =   base_url

        location_name = location['name'].encode('ascii', 'ignore').decode('ascii').strip()

        street_address = location['street'].encode('ascii', 'ignore').decode('ascii').strip()
        city =  location['city'].encode('ascii', 'ignore').decode('ascii').strip()
        state = location['region_code'].encode('ascii', 'ignore').decode('ascii').strip()
        zip = location['postal_code'].encode('ascii', 'ignore').decode('ascii').strip()
        phone = location['phone'].encode('ascii', 'ignore').decode('ascii').strip()
        country_code = location['country_id'].encode('ascii', 'ignore').decode('ascii').strip()
        store_number = location['store_number'].encode('ascii', 'ignore').decode('ascii').strip()
        location_type = ''

        latitude  = location['lat'].encode('ascii', 'ignore').decode('ascii').strip()
        longitude  = location['lng'].encode('ascii', 'ignore').decode('ascii').strip()

        hours_of_operation = BeautifulSoup(location['operation_hours'],"lxml").text.replace('\n','')

        page_url = '<MISSING>'
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
        store.append(page_url if page_url else '<MISSING>')
        #print('------',str(store))
        yield store
        i+=1


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
