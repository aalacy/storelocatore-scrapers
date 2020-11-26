import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time 
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('victoryma_com')



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = requests.get(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   elif method == "post":
       while True:
           try:
               if data:
                   r = requests.post(url,headers=headers,data=data)
               else:
                   r = requests.post(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   else:
       return None

def fetch_data():
    return_main_object = []
    address = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 600
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.volvocars.com/"
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        #logger.info(search.current_zip)
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        #logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        location_url = "https://liveapi.yext.com/v2/accounts/1342454/entities/geosearch?api_key=e3101b0a7c8f6bbd85f09c65cc1f29c7&v=20200630&location="+str(search.current_zip)+"&radius=500&countryBias=US&languages=en&limit=50"
        r = request_wrapper(location_url,"get",headers=headers)
        json_data1 = r.json()
        json_data = (json_data1['response']['entities'])
        for i in json_data:
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(str(i['name']).replace(' - Closed','') if i['name'] else "<MISSING>") 
            store.append(i['address']['line1'] if i['address']['line1'] else "<MISSING>")
            store.append(i['address']['city'] if i['address']['city'] else "<MISSING>")
            store.append(i['address']['region'] if i['address']['region'] else "<MISSING>")
            store.append(i['address']['postalCode'] if i['address']['postalCode'] else "<MISSING>")
            store.append(i['address']['countryCode'] if i['address']['countryCode'] else "<MISSING>")
            if "c_additionalID" in i:
                store.append(i['c_additionalID'] if i['c_additionalID'] else "<MISSING>")
            else:
                store.append("<MISSING>")
            store.append("<INACCESSIBLE>") 
            store.append("Volvo Cars")
            store.append(i['cityCoordinate']['latitude'] if i['cityCoordinate']['latitude'] else "<MISSING>")
            store.append(i['cityCoordinate']['longitude'] if i['cityCoordinate']['longitude'] else "<MISSING>")
            if "hours" in i:
                data_8 = str(i['hours']).replace("'","").replace(": {openIntervals: [{start: "," - ").replace(", end: "," - ").replace("}","").replace("{","").replace("[","").replace("]","").replace(", isClosed: False","").replace(": is"," - ").replace(': True',"")
                store.append(data_8 if data_8 else "<MISSING>")
            else:
                store.append("<MISSING>")
            if "c_newCarLocator" in i:
                store.append(i['c_newCarLocator'] if i['c_newCarLocator'] else "<MISSING>")
            else:
                store.append("<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store
        if current_results_len < MAX_RESULTS:
            #logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
