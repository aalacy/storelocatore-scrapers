# coding=UTF-8
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import requests
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
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
    MAX_RESULTS = 600
    MAX_DISTANCE = 20
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type':'application/json',
    }
    base_url = "https://www.walgreens.com"
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        page = 1
        while True:
            data = '{"lat":'+str(lat)+',"lng":'+str(lng)+',"requestType":"dotcom","s":"1000","p":"'+str(page)+'"}'
            r = requests.post("https://www.walgreens.com/locator/v1/stores/search", data=data, headers=headers).json()
            if "results" not in r:
                break
            current_results_len= len(r['results'])
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
            for location in r["results"]:
                storeNumber = location['store']['storeNumber']
                location_name = "Walgreens - Store #"+str(storeNumber)
                phone =location['store']['phone']['areaCode'] + ' '+ location['store']['phone']['number']
                storeNumber = location['storeNumber']
                latitude = location['latitude']
                longitude = location['longitude']
                zipp = location['store']['address']['zip']
                if zipp.replace("-","").strip().isdigit():
                    country_code = "US"
                else:
                    country_code = "CA"
                if phone.strip().lstrip():
                    phone = phone
                else:
                    phone = "<MISSING>"  

                page_url = "https://www.walgreens.com"+location['storeSeoUrl']
                r1 = requests.get(page_url ,headers=headers)
                soup = BeautifulSoup(r1.text,"lxml")
                try:
                    hours_of_operation = " ".join(list(soup.find("div",{"class":'service-section'}).find("li",{"class":'single-hours-lists'}).stripped_strings))
                except:
                    hours_of_operation = "<MISSING>"

                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, location['store']['address']['street'].capitalize(), location['store']['address']['city'].capitalize(), location['store']['address']['state'], zipp, country_code,
                        storeNumber, phone.strip(), location_type, latitude, longitude, hours_of_operation,page_url]

                if str(store[2]) in addresses:
                    continue
                addresses.append(str(store[2]) )

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("data =="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store
            page+=1
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
