# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time


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
    MAX_RESULTS = 60
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.foamortgage.com/"

    while zip_code:
        result_coords = []
        #print("zip_code === "+zip_code)
       # print("remaining zipcodes: " + str(len(search.zipcodes)))
        location_url = "https://api.2xlo.com//wp-json/foa/v1/search/branch/"+str(zip_code)+"?k=f007836b4b5907b824451e19faf63520b9daee20&radius=300"
        #print(location_url)
       
        r = session.get(location_url,headers=headers)
        data = r.json()
        if data['status'] == "failed":
            pass
        else:

            for value in data['results']:
            
                locator_domain = base_url
                location_name = value['branch_name']
                address = value['address']
                address2 = value['address2']
                street_address = address + " " + address2
                city = value['city']
                state = value['state']
                zipp = value['zip']
                store_number = value['id'].split("-")[-1]
                if value['branch_phone'] == "":
                    phone = "<MISSING>"
                else:
                    raw_phone = value['branch_phone']
                    phone = "(" + raw_phone[:3] + ") " + raw_phone[3:6] + "-" + raw_phone[6:]
                latitude = value['lat']
                longitude = value['lng']
                try:
                    day_span = value['branch_hours'][0]['day_span']
                    time_span = value['branch_hours'][0]['time_span']
                    hours_of_operation = day_span + ' - ' + time_span
                except:
                    hours_of_operation = "<MISSING>"
                #print(hours_of_operation)

                page_url = "https://www.foamortgage.com/branches/" + str(value['id']) + "/"

                result_coords.append((latitude, longitude))
                store = []
                store.append(locator_domain)
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
                store.append(page_url)
                if store[2] in adressess:
                    continue
                adressess.append(store[2])
                yield store

          #  print(len(data['results']))
       # print("==================")

        if len(data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()

def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)
scrape()
