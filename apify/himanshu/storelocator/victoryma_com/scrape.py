import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time 
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = requests.get(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   elif method == "post":
       while True:
           try:
               if data:
                   r = requests.post(url,headers=headers,data=data)
               else:
                   r = requests.post(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   else:
       return None

def fetch_data():
    return_main_object = []
    address = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 600
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.victoryma.com/"
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        #print(search.current_zip)
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        #print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        location_url = "https://www.victoryma.com/wp-admin/admin-ajax.php?action=store_search&lat="+str(lat)+"&lng="+str(lng)+"&max_results=10000&search_radius=5000&autoload=1"
        r = request_wrapper(location_url,"get",headers=headers)
        json_data = r.json()
        for i in json_data:
            hours_of_operation = " ".join(list(BeautifulSoup( i['hours'],'lxml').stripped_strings))
            city = i['city'].replace(',',"")
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(i['store'] if i['store'] else "<MISSING>") 
            store.append(i['address'] if i['address'] else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(i['state'] if i['state'] else "<MISSING>")
            store.append(i['zip'] if i['zip'] else "<MISSING>")
            store.append(i['country'] if i['country'] else "<MISSING>")
            store.append(i['id'] if i['id'] else "<MISSING>")
            store.append(i['phone'] if i['phone'] else"<MISSING>") 
            store.append("Victory Martial Arts")
            store.append(i['lat'] if i['lat'] else "<MISSING>")
            store.append(i['lng'] if i['lng'] else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(i['url'] if i['url'] else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store
        if current_results_len < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
