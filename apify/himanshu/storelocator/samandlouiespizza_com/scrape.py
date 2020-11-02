import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('samandlouiespizza_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object=[]
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
    base_url = 'https://samandlouiespizza.com/'
    location_type = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    nav  = soup.find('nav',{'id':'nav-main'}).find('li',class_='menu-item-1483').find('ul')
    for a in nav.find_all('a'):
        page_url= a['href']
        r_loc = session.get(page_url)
        soup_loc = BeautifulSoup(r_loc.text,'lxml')
        details = soup_loc.find('section',class_='store-detail')
        address = details.find('div',class_='detail-location').find('p').text.strip().split('|')
        if len(address) >2:
            street_address = address[1].strip()
        else:
            street_address = address[0].strip()
        city = address[-1].split(',')[0].strip()
        state = address[-1].split(',')[-1].split()[0].strip()
        zipp = address[-1].split(',')[-1].split()[-1].strip()
        location_name = city
        phone = details.find('div',class_='detail-contact').find('p').text.strip().replace('Phone:','').strip()
        hours_of_operation = details.find('div',class_='detail-contact').find('p',class_='hours').text.strip().replace('Hours:','').strip().replace('\n','  ')
        coords = details.find('div',class_='detail-contact').find('p',class_='hours').find_next('p').a['href'].split('@')
        if len(coords) !=1:
            latitude = coords[-1].split(',')[0].strip()
            longitude =   coords[-1].split(',')[1].strip()
        else :
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        
        

    
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
