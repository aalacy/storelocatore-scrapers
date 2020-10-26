# coding=UTF-8

import csv
import requests
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
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
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 25
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }

    base_url = "https://www.davita.com/"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # print(search.current_zip)
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
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
        location_url = "https://www.davita.com/api/find-a-center?location="+str(search.current_zip)+"&lat="+str(lat)+"&lng="+str(lng)+"&modalities=0&p=0"

        r = session.get(location_url, headers=headers, verify=False).json()
        if r['locations'] != None:
            current_results_len = (len(r['locations'])) 
            for data in r['locations']:
                location_name = data['facilityname']
                street_address = (data['address']['address1'] +" "+ str(data['address']['adress2'])).strip()
                city = data['address']['city']
                state = data['address']['state']
                zipp = data['address']['zip']
                latitude = data['address']['latitude']
                longitude = data['address']['longitude']
                store_number = data['facilityid']
                phone = data['phone']
                
                page_url = "https://www.davita.com/locations/"+str(state.lower())+"/"+str(city.lower())+"/"+str(data['address']['address1'].replace(" ","-").lower())+"--"+str(store_number)
                # print(page_url)       
    
                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if str(store[2]) in addresses:
                    continue
                addresses.append(str(store[2]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
        else:
            pass

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
