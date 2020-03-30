import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():


    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 25
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    base_url = "https://www.nathansfamous.com"
    headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"}
    output = []
    while zip_code:
        result_coords =[]
        try:
            r = session.get("https://locator.smfmsvc.com/api/v1/locations?client_id=156&brand_id=ACTP&product_id=ANY&product_type=agg&zip="+str(search.current_zip)+"&search_radius="+str(MAX_DISTANCE),headers=headers).json()
        except:
            continue
        
        
        # if "STORE" not in r['RESULTS']['STORES']:
        #     continue
        if "STORE" in r['RESULTS']['STORES']:
            current_results_len = len(r['RESULTS']['STORES']['STORE'])
            for loc in r['RESULTS']['STORES']['STORE']:
                
                if type(loc)==str:
                    continue


                hour=''
                address=loc['ADDRESS']
                city=loc['CITY']
                lat=loc['LATITUDE']
                lng=loc['LONGITUDE']
                name=loc['NAME']
                storeno=loc['STORE_ID']
                zip=loc['ZIP']
                country="US"
                state=loc['STATE']
                phone=loc['PHONE']
                page_url=''
                store=[]
                result_coords.append((lat, lng))
                store.append(base_url)
                store.append(name if name else "<MISSING>")
                store.append(address if address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zip if zip else "<MISSING>")
                store.append(country if country else "<MISSING>")
                store.append(storeno if storeno else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour else "<MISSING>")
                store.append(page_url if page_url else "<MISSING>")
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # print("store-------------",store)
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
