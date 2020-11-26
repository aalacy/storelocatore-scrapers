# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('watermillexpress_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 25
    current_results_len = 0 
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "http://www.watermillexpress.com"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        #logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        location_url ="http://www.watermillexpress.com/wp-admin/admin-ajax.php?action=store_search&lat="+str(lat)+"&lng="+str(lng)+"&max_results=25&search_radius=25&search=&statistics="
        try:

             r_locations = session.get(location_url, headers=headers)
        except:
            continue

        json_data = r_locations.json()

        current_results_len = int(len(json_data))  

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
        hours_of_operation = "<MISSING>"
        page_url = "http://www.watermillexpress.com/wp-admin/admin-ajax.php?action=store_search&lat="+str(lat)+"&lng="+str(lng)+"&max_results=25&search_radius=25&search=&statistics="

        for location in json_data:
			
            city=location["city"]
            state=location["state"]
            zipp=location["zip"]
            address2= location['address2']
            street_address= location['address'] + " "+str(address2).replace('None','')
            latitude=location["lat"]
            longitude=location["lng"]
            phone=location["phone"]
            store_number=location["store"]


            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x.strip() if x else "<MISSING>" for x in store]
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
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
