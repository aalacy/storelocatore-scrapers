import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('snappysalads_com')




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
    return_main_object = []
    base_url = 'https://www.snappysalads.com'
    data_url = "https://www.snappysalads.com/hours-and-locations"
    

    r = session.get(data_url)
    soup=BeautifulSoup(r.text,'lxml')
    main = soup.find('main',class_='site-content__main').find_all('script')[-1].text.split('locations:')[-1].split('}}]')[0] + '}}]'
    json_data = json.loads(main)
    for loc in json_data:
        country_code = "US"
        location_type  = "<MISSING>"
        location_name = loc['name']
        page_url  = base_url + loc['url']
        hours_of_operation = BeautifulSoup(loc['hours'],'lxml').p.text.strip()
        store_number = loc['id']
        street_address =loc['street']
        city = loc['city']
        state = loc['state']
        zipp= loc['postal_code']
        phone = loc['phone_number'].replace(' (SNAP)','')
        latitude= loc['lat']
        longitude = loc['lng']
        
        store=[]
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        return_main_object.append(store)
        # logger.info(str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object       
            

        
        
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
