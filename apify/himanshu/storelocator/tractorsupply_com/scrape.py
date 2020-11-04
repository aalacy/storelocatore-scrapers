import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tractorsupply_com')


session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    zip_code = search.next_zip()

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.tractorsupply.com/"

    while zip_code:
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        result_coords = []
        json_data = session.get("https://www.tractorsupply.com/wcs/resources/store/10151/zipcode/fetchstoredetails?zipCode="+str(zip_code)+"&isOverlay=Y&lpStoreId=&storeId=&catalogId=&langId=&responseFormat=json&_=1591770815402", headers=headers).json()['storesList']
        
        for data in json_data:

            location_name = data['storeName'].capitalize()
            street_address = data['addressLine']
            city = data['city']
            state = data['state']
            zipp = data['zipCode']
            store_number = data['stlocId']
            country_code =  data['country']
            phone = data['phoneNumber']
            lat = data['latitude']
            lng = data['longitude']
            hours = data['storeHours'].replace("="," ").replace("|"," ")
            page_url = "https://www.tractorsupply.com/tsc/store_"+str(location_name.replace(" ","").replace(state,"").strip())+"-"+str(state)+"-"+str(zipp)+"_"+str(store_number)

        
        
            result_coords.append((lat,lng))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number) 
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])  
            store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store

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
