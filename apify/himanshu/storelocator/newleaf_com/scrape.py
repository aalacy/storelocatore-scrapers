import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup 
import re
import json
import sgzip
import time 
from datetime import datetime
import time
session = SgRequests()
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
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object = []
    address = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0     
    zip_code = search.next_zip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.newleaf.com/"
    location_url = "https://www.newleaf.com/wp-admin/admin-ajax.php?action=get-stores-with-extras&terms=&lat=36.989602&lng=-121.997219&radius="
    r = session.get(location_url,headers=headers).json()
    a = r['store-30330']
    b = r['store-30327']
    c = r['store-30323']
    d = r['store-30319']
    e = r['store-30316']
    location_name  = (a['title'])
    street_address = (a['address'])
    city = (a['city'])
    state = (a['state'])
    country_code = "US"
    latitude = (a['lat'])
    longitude = (a['lng'])
    page_url= (a['permalink'])
    store_number = "30330"
    phone = (a['phone'])
    location_type ="<MISSING>"
    hours_of_operation =(a['hours'])
    zipp = "95060"
    store = []
    store.append(base_url if base_url else "<MISSING>")
    store.append(location_name if location_name else "<MISSING>") 
    store.append(street_address if street_address else "<MISSING>")
    store.append(city if city else "<MISSING>")
    store.append(state if state else "<MISSING>")
    store.append(zipp if zipp else "<MISSING>")
    store.append(country_code if country_code else "<MISSING>")
    store.append(store_number if store_number else"<MISSING>") 
    store.append(phone if phone else "<MISSING>")
    store.append(location_type if location_type else "<MISSING>")
    store.append(latitude if latitude else "<MISSING>")
    store.append(longitude if longitude else "<MISSING>")
    store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
    store.append(page_url if page_url else "<MISSING>")
    yield store
    location_name  = (b['title'])
    street_address = (b['address'])
    city = (b['city'])
    state = (b['state'])
    country_code = "US"
    latitude = (b['lat'])
    longitude = (b['lng'])
    page_url= (b['permalink'])
    store_number = "30327"
    phone = (b['phone'])
    location_type ="<MISSING>"
    hours_of_operation =(b['hours'])
    zipp = "94019"
    store = []
    store.append(base_url if base_url else "<MISSING>")
    store.append(location_name if location_name else "<MISSING>") 
    store.append(street_address if street_address else "<MISSING>")
    store.append(city if city else "<MISSING>")
    store.append(state if state else "<MISSING>")
    store.append(zipp if zipp else "<MISSING>")
    store.append(country_code if country_code else "<MISSING>")
    store.append(store_number if store_number else"<MISSING>") 
    store.append(phone if phone else "<MISSING>")
    store.append(location_type if location_type else "<MISSING>")
    store.append(latitude if latitude else "<MISSING>")
    store.append(longitude if longitude else "<MISSING>")
    store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
    store.append(page_url if page_url else "<MISSING>")
    yield store  
    location_name  = (c['title'])
    street_address = (c['address'])
    city = (c['city'])
    state = (c['state'])
    country_code = "US"
    latitude = (c['lat'])
    longitude = (c['lng'])
    page_url= (c['permalink'])
    store_number = "30323"
    phone = (c['phone'])
    location_type ="<MISSING>"
    hours_of_operation =(c['hours'])
    zipp = "95060"
    store = []
    store.append(base_url if base_url else "<MISSING>")
    store.append(location_name if location_name else "<MISSING>") 
    store.append(street_address if street_address else "<MISSING>")
    store.append(city if city else "<MISSING>")
    store.append(state if state else "<MISSING>")
    store.append(zipp if zipp else "<MISSING>")
    store.append(country_code if country_code else "<MISSING>")
    store.append(store_number if store_number else"<MISSING>") 
    store.append(phone if phone else "<MISSING>")
    store.append(location_type if location_type else "<MISSING>")
    store.append(latitude if latitude else "<MISSING>")
    store.append(longitude if longitude else "<MISSING>")
    store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
    store.append(page_url if page_url else "<MISSING>")
    yield store
    location_name  = (d['title'])
    street_address = (d['address'])
    city = (d['city'])
    state = (d['state'])
    country_code = "US"
    latitude = (d['lat'])
    longitude = (d['lng'])
    page_url= (d['permalink'])
    store_number = "30319"
    phone = (d['phone'])
    location_type ="<MISSING>"
    hours_of_operation =(d['hours'])
    zipp = "95010"
    store = []
    store.append(base_url if base_url else "<MISSING>")
    store.append(location_name if location_name else "<MISSING>") 
    store.append(street_address if street_address else "<MISSING>")
    store.append(city if city else "<MISSING>")
    store.append(state if state else "<MISSING>")
    store.append(zipp if zipp else "<MISSING>")
    store.append(country_code if country_code else "<MISSING>")
    store.append(store_number if store_number else"<MISSING>") 
    store.append(phone if phone else "<MISSING>")
    store.append(location_type if location_type else "<MISSING>")
    store.append(latitude if latitude else "<MISSING>")
    store.append(longitude if longitude else "<MISSING>")
    store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
    store.append(page_url if page_url else "<MISSING>")
    yield store
    location_name  = (e['title'])
    street_address = (e['address'])
    city = (e['city'])
    state = (e['state'])
    country_code = "US"
    latitude = (e['lat'])
    longitude = (e['lng'])
    page_url= (e['permalink'])
    store_number = "30316"
    phone = (e['phone'])
    location_type ="<MISSING>"
    hours_of_operation =(e['hours'])
    zipp = "95003"
    store = []
    store.append(base_url if base_url else "<MISSING>")
    store.append(location_name if location_name else "<MISSING>") 
    store.append(street_address if street_address else "<MISSING>")
    store.append(city if city else "<MISSING>")
    store.append(state if state else "<MISSING>")
    store.append(zipp if zipp else "<MISSING>")
    store.append(country_code if country_code else "<MISSING>")
    store.append(store_number if store_number else"<MISSING>") 
    store.append(phone if phone else "<MISSING>")
    store.append(location_type if location_type else "<MISSING>")
    store.append(latitude if latitude else "<MISSING>")
    store.append(longitude if longitude else "<MISSING>")
    store.append(hours_of_operation.strip() if hours_of_operation else "<MISSING>")
    store.append(page_url if page_url else "<MISSING>")
    yield store  
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
