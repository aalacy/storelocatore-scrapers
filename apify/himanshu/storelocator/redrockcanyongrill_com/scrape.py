import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('redrockcanyongrill_com')





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
    base_url = 'https://www.redrockcanyongrill.com/'
    location_type = "<MISSING>"
    country_code = "US"
    url= "https://www.redrockcanyongrill.com/locations/"
    r = session.get(url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    script = soup.find('div',class_='location-finder').find_next('script').text.split('var guteLocations =')[-1]
    json_data = json.loads(script)
    for info in json_data:
        store_number = info['ID']
        page_url = info['link']
        latitude = info['lat']
        longitude = info['long']
        r_loc= session.get(page_url,headers = headers)
        soup_loc = BeautifulSoup(r_loc.text,'lxml')
        location_name = soup_loc.find('h1',class_='title has-text-centered').text.strip().replace('|',',').strip()
        address= soup_loc.find('address',class_='address').text.strip()
        list_address= re.sub(' +', ' ', address).split(',')
        street_address = list_address[0].strip()
        city = list_address[1].strip()
        state = list_address[-1].split()[0].strip()
        zipp= list_address[-1].split()[-1].strip()
        phone = soup_loc.find('p',class_='phone').text.strip()
        hours_of_operation = soup_loc.find('div',class_='hours').text.strip().replace('\n','    ')
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
