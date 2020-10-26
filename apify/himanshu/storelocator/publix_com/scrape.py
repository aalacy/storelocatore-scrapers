import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('publix_com')




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
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.publix.com"

    while zip_code:
        result_coords = []

        # logger.info("zip_code === "+zip_code)

        location_url = "https://services.publix.com/api/v1/storelocation?zipCode="+str(zip_code)
        
        try:
            r = session.get(location_url,headers=headers).json()
        except:
            continue
        current_results_len = len(r['Stores'])

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""

        for i in r['Stores']:
            location_name = i['NAME']
            street_address = i['ADDR']
            city = i['CITY']
            state = i['STATE']
            zipp = i['ZIP']
            country_code = "US"
            store_number = i['KEY']
            phone = i['PHONE']
            location_type = i['TYPE']
            latitude = i['CLAT']
            longitude = i['CLON']
            hours_of_operation = i['STRHOURS']
            page_url = "https://www.publix.com/locations/"+i['KEY']+"-"+str(location_name.lower().replace(' ','-'))
    

       

            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if store[2] + store[-3] in addresses:
                continue

            addresses.append(store[2] + store[-3])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

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
