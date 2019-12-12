import csv
import sys

import requests
from bs4 import BeautifulSoup
import re
import json
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
import sgzip


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url",])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.wawa.com"

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 200000
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()    # zip_code = search.next_zip()    
    
    while coord:
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
        location_type = ""
        latitude = ""
        longitude = ""
        hours_of_operation = ""
        lat = coord[0]
        lng = coord[1]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        # lat = -42.225
        # lng = -42.225
        # zip_code = 11576
        # print('location_url ==' +location_url))
        
        try:
            location_url = "https://www.wawa.com/Handlers/LocationByLatLong.ashx?limit="+str(MAX_RESULTS)+"&lat="+str(lat)+"&long="+str(lng)
            k = requests.get(location_url, headers=headers).json()
        except:
            continue
    

        
        if "locations" in k:
            current_results_len =len(k['locations'])
            # print("==============",current_results_len)
            for index,i in enumerate(k['locations']):
                street_address = i['addresses'][0]['address']
                city = i['addresses'][0]['city']
                state = i['addresses'][0]['state']
                zipp = i['addresses'][0]['zip']
                lat = i['addresses'][1]['loc'][0]
                lng = i['addresses'][1]['loc'][1]
                phone = i['telephone']
                hours_of_operation = i['openType']
                store_number = i['storeNumber']
                location_name = '<MISSING>'
                latitude = lat
                longitude = lng
                page_url = "https://www.wawa.com/about/locations/store-locator"
                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address.encode('ascii', 'ignore').decode('ascii').strip().replace(" (@",""), city.encode('ascii', 'ignore').decode('ascii').strip(), state.encode('ascii', 'ignore').decode('ascii').strip(), zipp.encode('ascii', 'ignore').decode('ascii').strip(), country_code,
                        store_number, phone.encode('ascii', 'ignore').decode('ascii').strip(), location_type, latitude, longitude, hours_of_operation.encode('ascii', 'ignore').decode('ascii').strip(),page_url]

                # store = [locator_domain, location_name.strip(), street_address.strip().replace(" (@",""), city.strip(), state, zipp.strip(), country_code,
                #         store_number, phone.strip(), location_type, latitude, longitude, hours_of_operation.strip(),page_url]

            
                if str(store[2]) + str(store[-3]) not in addresses:
                    addresses.append(str(store[2]) + str(store[-3]))                   
                    store = [x if x else "<MISSING>" for x in store]
                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store

            if current_results_len < MAX_RESULTS:
                # print("max distance update")
                search.max_distance_update(MAX_DISTANCE)
            elif current_results_len == MAX_RESULTS:
                # print("max count update")
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " + str(MAX_RESULTS) + " results")

        coord = search.next_coord()   # zip_code = search.next_zip()    
        # break

def scrape():
    data = fetch_data()

    write_output(data)


scrape()
