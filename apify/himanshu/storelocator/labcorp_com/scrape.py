# coding=UTF-8

import csv
from  sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.labcorp.com/"

    while coord:
        result_coords = []
      #  print(search.current_zip)
       # print("remaining zipcodes: " + str(len(search.zipcodes)))
        location_url = "https://www.labcorp.com/labs-and-appointments/results?lat="+str(coord[0])+"&lon="+str(coord[1])+"&radius="+str(MAX_DISTANCE)
        # print(location_url)
        try:
            r = session.get(location_url, headers=headers)
        except:
            pass
        
        soup = BeautifulSoup(r.text, "lxml") 
        data = soup.find("script",{"type":"application/json"}).text
        json_data = json.loads(data)
        if "lc_psc_locator" in json_data:
            if "psc_locator_app" in json_data['lc_psc_locator']:
                current_results_len = len(json_data['lc_psc_locator']['psc_locator_app']['settings']['labs'])
                #print(current_results_len)
                for i in json_data['lc_psc_locator']['psc_locator_app']['settings']['labs']:  
                     
                    location_name = i['name']
                    store_number = i['locatorId']
                    street_address = i['address']['street']
                    city = i['address']['city']
                    state = i['address']['stateAbbr']
                    zipp = i['address']['postalCode']
                    phone = i['phone']
                    latitude = i['address']['lat']
                    longitude = i['address']['lng']
                    hours_of_operation = i['hours']

                    result_coords.append((latitude, longitude))
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append("US")
                    store.append(store_number) 
                    store.append(phone)
                    store.append("<MISSING>")
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours_of_operation)
                    store.append("<MISSING>")
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    yield store
            else:
                current_results_len = 0
                pass
        else:
            current_results_len = 0
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
