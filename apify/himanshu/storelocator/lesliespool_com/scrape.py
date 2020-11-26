import csv
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lesliespool_com')




session = SgRequests()

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    }

    base_url = "https://www.lesliespool.com"
    r =  session.get("https://lesliespool.com/on/demandware.store/Sites-lpm_site-Site/en_US/Stores-FindStores?showMap=false&radius=500000&pools=false&service=false&countryCode=US", headers=headers).json()
    
    for dt in r['stores']:
        page_url=''
        if dt['contentAssetId']:
            page_url = "https://lesliespool.com/"+dt['contentAssetId']+".html"
        location_name = dt['name'].lower()
        street_address =''
        street_address1=''
        if dt['address2']:
            street_address1 =  dt['address2'].lower()
        street_address = dt['address1'].lower() + ' '+street_address1
        city = dt['city'].lower()
        zipp = dt['postalCode']
        state = dt['stateCode']
        if dt['latitude']==0:
            latitude=''
            longitude=''
        else:
            latitude = dt['latitude']
            longitude = dt['longitude']

        hours_of_operation = dt['storeHours'].replace("*",' ')
        phone = dt['phone']
        
   
      
        store = []
        store.append(base_url)
        store.append(location_name.replace("#"+str(dt['ID']),''))
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(dt['ID'])
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation.replace("Hours not scheduled for this gro",''))
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # logger.info("data===="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        # print("store:--- ",store)
        yield store

      


def scrape():
    data = fetch_data()
    write_output(data)


scrape()