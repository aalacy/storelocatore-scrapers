import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('renault_co_uk')


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
    MAX_RESULTS = 50
    MAX_DISTANCE = 20
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['UK'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []
    
    base_url = "https://www.renault.co.uk/"
    
    while zip_code:
        result_coords =[]
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))

        url = "https://dealerlocator.renault.co.uk/data/GetDealersList"
        payload = 'postcode='+str(zip_code)
        headers = {
        'Host': 'dealerlocator.renault.co.uk',
        'Origin': 'https://dealerlocator.renault.co.uk',
        'Referer': 'https://dealerlocator.renault.co.uk/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        }
        try:
            response = requests.request("POST", url, headers=headers, data = payload).json()
        except:
            pass
        if "Result" in response:
            for data in response['Result']['Dealers']:
                street_address1=''
                location_name = data['DealerName']
                street_address1 = data['AddressLine1']
                if street_address1:
                    street_address1=street_address1
                street_address =street_address1+ ' '+ data['AddressLine2']
                city = data['Town']
                state = "<MISSING>"
                zipp = data['PostCode']
                phone = data['Phone']
                lat = data['Latitude']
                lng = data['Longitude']
                page_url = data['Website']
                store_number = "<MISSING>"
                hours=""
                if data['OpeningHours'] != None:
                    for h in data['OpeningHours']:
                        # logger.info(h)
                        if h["Value"] != None:
                            if h["Value"]:
                                hours = hours+ ' '+h["Label"]+ ' '+h["Value"]
                else:
                    hours = "<MISSING>"
                result_coords.append((lat,lng))
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append("UK")
                store.append(store_number)
                store.append(phone)
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                store.append(hours if hours else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")     
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if store[2] in adressess:
                    continue
                adressess.append(store[2])
                #logger.info(store)
                yield store

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
