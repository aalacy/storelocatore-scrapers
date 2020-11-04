import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



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
    base_url = "https://teriyakimadness.com/"
    location_url  = 'https://teriyakimadness.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=f73df18e58&load_all=1&layout=1'
    r = session.get(location_url ,headers = header).json()
    for idx, val in enumerate(r):

       
        if len(val['street']) > 0:

            locator_domain = base_url
            if "Coming Soon!" in val['title']:
                continue
            location_name =  val['title'].replace("<br>"," ")
            street_address = val['street'].strip()
            city = val['city'].strip()
            state = val['state'].strip()
            if "03920" in val['postal_code']:
                continue
            zip = val['postal_code'].strip()
            store_number = '<MISSING>'
            country_code = val['country'].strip()
            phone = val['phone'].strip()
            location_type = '<MISSING>'
            latitude = val['lat'].strip()
            longitude = val['lng'].strip()
            ck = json.loads(val['open_hours'])
            page_url = val['website']
            gb = []
            for idx, bk in enumerate(ck):
                
                for idx, val in enumerate(ck[bk]):
                
                    gb.append(''.join(list(bk +':'+ val)))

            
            hours_of_operation = ' '.join(gb)
           
            
            store=[]
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name.strip() if location_name else '<MISSING>')
            store.append(street_address.strip() if street_address else '<MISSING>')
            store.append(city.strip() if city else '<MISSING>')
            store.append(state.strip() if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            
            store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
            store.append(page_url  if page_url else '<MISSING>')

            

            return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)

scrape()
