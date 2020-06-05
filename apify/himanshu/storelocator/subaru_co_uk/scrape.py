import csv
import requests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
import time
from sgrequests import SgRequests
session = SgRequests() 
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['gb'])
    MAX_RESULTS = 100
    MAX_DISTANCE = 50
    coord = search.next_coord()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "https://www.subaru.co.uk/"
    while coord:
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        result_coords = []
        json_data = requests.get("https://www.subaru.co.uk/wp-admin/admin-ajax.php?action=store_search&lat="+str(coord[0])+"&lng="+str(coord[1])+"&max_results=100&search_radius=500&autoload=1",headers=headers).json()

        for data in json_data:
            print(data)
            location_name  = data['store']
            street_address = data['address']
            city = data['city']
            state = data['state']
            zipp = data['zip']
            country_code = data['country']
            phone =  data['phone']
            lat = data['lat']
            lng = data['lng']
            page_url = data["url"]
            store_number = data['id']

            if data['hours']:
                hours = " ".join(list(bs(data['hours'],"lxml").find("table").stripped_strings))
            else:
                hours = "<MISSING>"
            

            result_coords.append((lat,lng))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("UK")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)     
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store 

        if len(json_data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
