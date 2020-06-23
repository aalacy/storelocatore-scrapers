import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests
from datetime import datetime
import sgzip
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess =[]
    MAX_RESULTS = 50
    MAX_DISTANCE = 40
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    
    payload = {}
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    }
    while zip_code:
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print("zipcode",zip_code)
        count=0
        while True:
            r = requests.get("https://www.plowhearth.com/en/store-finder?q="+str(zip_code)+"&page="+str(count),headers=headers).json()
            if r['total']==0:
                break
            result_coords=[]
            count +=1
            current_results_len=len(r['data'])
            for q in r['data']:
                lat = q['latitude']
                log = q['longitude']
                address1=''
                address1 = q['line2']
                if address1:
                    address1=address1
                address = q['line1']+ ' '+address1
                city = q['town']
                state = q['state']
                zipp = q['postalCode']
                phone = q['phone']
                page_url= "https://www.plowhearth.com"+q['url']
                name= q['displayName']
                try:
                    hours=' '.join('{} : {}'.format(key, value) for key, value in q['openings'].items())
                except:
                    hours="<MISSING>"
                store = []
                store.append("https://www.plowhearth.com/")
                store.append(name)
                store.append(address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("<MISSING>")
                store.append(lat)
                store.append(log)
                result_coords.append((lat, log))
                store.append(hours)
                store.append(page_url)
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                print(str(store))
                print('======================')
                # print(store)
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store
        
        if current_results_len < MAX_RESULTS:
                # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
   

def scrape():
    data = fetch_data()
    write_output(data)

scrape()



