# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('roostersmgc_com')





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
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.roostersmgc.com"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        #logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        try:
            get_url ="https://info3.regiscorp.com/salonservices/siteid/43/salons/searchGeo/map/"+str(lat)+"/"+str(lng)+"/0.8/0.5/true"
           
            # location_url = "https://info3.regiscorp.com/salonservices/siteid/43/salons/searchGeo/map/"+str(lat)+"/"+str(lng)+"/90/180/true"
            r = session.get(get_url, headers=headers)
        except:
            continue
        # r_utf = r.text.encode('ascii', 'ignore').decode('ascii')
        # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")

        json_data = r.json()
        
        
        # json_data = json.loads(r_utf)
        # logger.info("json_Data === " + str(json_data))
        current_results_len = int(len(json_data['stores']))
        # logger.info(json_data)
        # logger.info(current_results_len) # it always need to set total len of record.
        # logger.info("current_results_len === " + str(current_results_len))

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
        
        for location in json_data['stores']:
            street_address = location['subtitle']
            
            longitude = location['longitude']
            latitude = location['latitude']
            location_name = location['title']
            store_hours = location['store_hours']
            if "phonenumber" in location:
                phone = location['phonenumber'].replace("(0) 0-0","<MISSING>")
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(street_address))

            state_list = re.findall(r' ([A-Z]{2}) ', str(street_address))

            if us_zip_list:
                zipp = us_zip_list[-1]

            if state_list:
                state = state_list[-1]

            hours_of_operation = ''
            for i in store_hours:
                hours_of_operation = hours_of_operation +' '+ i['days'] + ' ' +i['hours']['open']+' '+ i['hours']['close']

            
            
            street_address1 = street_address.replace(zipp,"").replace(state,"").lstrip(",").split(",")[0]
            
            city =  " ".join(street_address.replace(zipp,"").replace(state,"").lstrip(",").split(",")[1:]).replace(",","")
            #logger.info("street_address1",city)
            
            street_address2 = street_address1.split("  ")[0]
            # logger.info("|================",street_address2.split("  "))
            page_url = "<MISSING>"
            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address2, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,get_url]

            if store[2] in addresses:
                continue
        
            addresses.append(store[2])

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

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
        coord = search.next_coord()
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
