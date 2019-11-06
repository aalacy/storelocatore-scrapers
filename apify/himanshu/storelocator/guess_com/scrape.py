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
        "Authorization":"R8-Gateway App=shoplocal, key=guess, Type=SameOrigin",
        "Referer":"https://guess.radius8.com/sl/shoplocal_guess?r8dref=fcbb573a-fd5c-b3d7-bb9c-43a060fe3db4&r8sl_store_code=5023&r8view=locations&",
        "X-Device-Id":"fcbb573a-fd5c-b3d7-bb9c-43a060fe3db4",
        "X-Domain-Id":'guess'
    }
    base_url = "https://shop.guess.com/"
    page_url = "<MISSING>"
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 30000
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()    # zip_code = search.next_zip()    
    
    while coord:
        result_coords = []
        locator_domain = 'https://guess.com/'
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        # country_code = "US"
        store_number = "<MISSING>"
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        lat = coord[0]
        lng = coord[1]
        location_url = "https://guess.radius8.com/api/v1/streams/stores?lat="+str(lat)+"&lng="+str(lng)+"&radius="+str(MAX_DISTANCE)+"&units=MI&limit="+str(MAX_RESULTS)+"&divisions=guess&_ts=1569414026314"
        
        try:
            k = requests.get(location_url, headers=headers).json()
        except:
            continue
        current_results_len = len(k)
        if "results" in k:
            for i  in k['results']:
                location_name = i['name']
                street_address = i['address']['address1']
                city = i['address']['city']
                zipp = i['address']['postal_code']
                if len(zipp)==6 or len(zipp)==7:
                    country_code = "CA"
                else:
                    country_code = "US"
                if "state" in i['address']:
                    state =i['address']['state']
                else:
                    state = "<MISSING>"
                lat = i['geo_point']['lat']
                lng = i['geo_point']['lng']
                phone = i['contact_info']['phone']
                time = ''
                kk = []
                for x in i['hours']:
                    kk.append(x + " " + i['hours'][x][0][:2]+':'+i['hours'][x][0][2:4] +" AM to PM " + i['hours'][x][1][:2]+':'+i['hours'][x][1][2:4])
                hours_of_operation = ' '.join(kk)
                latitude =  lat
                longitude = lng
                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                if str(store[2]) + str(store[-4]) not in addresses:
                    addresses.append(str(store[2]) + str(store[-4]))                   
                    store = [x if x else "<MISSING>" for x in store]
                    #print("data = " + str(store))
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
