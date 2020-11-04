# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import warnings
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('busey_com')






session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresseees =[]
    return_main_object = []
    store_detail  = []
    addresses = []
    addresses1 = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 1000
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.busey.com/"

    while coord:
        locator_domain = base_url
        location_name ="<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type ="<MISSING>"
        latitude = "<MISSING>"
        longitude ="<MISSING>"
        raw_address ="<MISSING>"
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        #logger.info(search.current_zip)
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        try:
            location_url = "https://www.busey.com/_/api/branches/"+str(lat)+"/"+str(lng)+"/500"
            r = session.get(location_url, headers=headers)
            json_data = r.json()
        except:
            pass
        
        hours_of_operation = ""
        for location in json_data["branches"]:
            soup = BeautifulSoup(location['description'], "lxml")
            hours_of_operation = " ".join(list(soup.stripped_strings)).split("Available")[0]
            location_type = 'branch'
            result_coords.append((str(location['lat']),  str(location['long'])))
            store = []
            store = [locator_domain, location['name'], location['address'], location['city'], location['state'], location['zip'], country_code,
                     store_number, location['phone'], location_type, str(location['lat']), str(location['long']), hours_of_operation,"<MISSING>"]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))
                store = [x.strip() if x else "<MISSING>" for x in store]
                #logger.info("data = " + str(store))
                #logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
    
        try:
            location_url1 = "https://www.busey.com/_/api/atms/"+str(lat)+"/"+str(lng)+"/500"
            r1 = session.get(location_url1, headers=headers)
            json_data1 = r1.json()
        except:
            pass
        
        for location1 in json_data1["atms"]:
            hours_of_operation = ""
            location_type = 'ATM'
            result_coords.append((str(location1['lat']),  str(location1['long'])))
            store1 =[]
            store1 = [locator_domain, location1['name'], location1['address'], location1['city'], location1['state'], location1['zip'], country_code,
                     store_number, phone, location_type, str(location1['lat']), str(location1['long']), hours_of_operation,"<MISSING>"]
            if str(store1[2]) + str(store1[-3]) not in addresses1:
                addresses1.append(str(store1[2]) + str(store1[-3]))
                store1 = [x.strip() if x else "<MISSING>" for x in store1]
                #logger.info("data = " + str(store))
                #logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store1
         

        current_results_len = len(json_data['branches'])+ len(json_data1['atms'])
        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

   

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
