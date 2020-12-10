import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kia_com')


session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []
    
    base_url = "https://www.kia.com/"
    
    while zip_code:
        result_coords =[]
        # logger.info("zip_code === "+zip_code)
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        location_url = "https://www.kia.com/us/services/en/dealers/search"

        data = r'{"type":"zip","zipCode":"'+str(zip_code)+'","dealerCertifications":[],"dealerServices":[]}'
        try:
            json_data = session.post(location_url, data=data).json()
        except:
            pass
        for store in json_data:
            
            location_name = store['name']
            street_address = store['location']['street1']
            city = store['location']['city']
            state = store['location']['state']
            zipp = store['location']['zipCode']
            phone = store['phones'][0]['number']
            lat = store['location']['latitude']
            lng = store['location']['longitude']
            store_number = store['code'].replace(state,"")
            page_url = store['url'].lower()
            # logger.info(page_url)
            hours = ""
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
            hours = "<MISSING>"
            hours='<INACCESSIBLE>'
            
    
            result_coords.append((lat,lng))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours if hours else "<MISSING>")
            store.append(page_url)     
            if store[2] in adressess:
                continue
            adressess.append(store[2]) 
            store = [str(x).strip() if x else "<MISSING>" for x in store]

            yield store
        
            # logger.info(store)
        # logger.info(len(json_data))

        if len(json_data) < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
