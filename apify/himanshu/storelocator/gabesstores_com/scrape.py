import csv
import sys

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gabesstores_com')





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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.gabesstores.com"

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 100
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()     
    while zip_code:
        result_coords = []
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""

        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        # lat = -42.225
        # lng = -42.225

        # zip_code = 11576
        
        # logger.info('location_url ==' +location_url))
        # logger.info("===============================================",zip_code)
        
        location_url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius="+str(MAX_DISTANCE)+"&location="+zip_code+"&limit="+str(MAX_RESULTS)+"&api_key=56bb34af25f122cb7752babc1c8b9767&v=20181201&resolvePlaceholders=true&entityTypes=location"
        k = session.get(location_url, headers=headers).json()
        current_results_len = len(k['response']['entities'])
        for i in k['response']['entities']:
            street_address =i["address"]['line1']
            city = i["address"]['city']
            state =  i["address"]['region']
            zipp = i["address"]['postalCode']
            location_name = i["name"]
            phone = i['mainPhone']
            # time = ''
            # for j in i["hours"].keys():
            #     if "openIntervals" in i["hours"][j]: 
            #         time = time +' ' + (j + ' ' +i["hours"][j]['openIntervals'][-1]["start"]+ ' ' + i["hours"][j]['openIntervals'][-1]["end"])
          
            # logger.info("=============================",i["hours"])
            # hours_of_operation =time
            latitude = i['yextDisplayCoordinate']['latitude']
            longitude = i['yextDisplayCoordinate']['longitude']
            # page_url = i['landingPageUrl']
            if "landingPageUrl" in i:
                page_url =i['landingPageUrl']
                k1 = session.get(page_url, headers=headers)
                soup2 = BeautifulSoup(k1.text, "html.parser")
                time = (" ".join(list(soup2.find("tbody",{"class":"hours-body"}).stripped_strings)))
            else:
                page_url = "<MISSING>"
            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, time,page_url]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))                   
                store = [x if x else "<MISSING>" for x in store]
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
        # coord = search.next_coord()   # zip_code = search.next_zip()    
        zip_code = search.next_zip()
        # break

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
