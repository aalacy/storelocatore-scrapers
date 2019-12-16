import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.publix.com"
    while zip_code:
        result_coords = []

        # print("zip_code === "+zip_code)
        location_url ="https://services.publix.com/api/v1/storelocation?types=&option=&includeOpenAndCloseDates=true&zipCode="+str(zip_code)
        # location_url = "https://services.publix.com/api/v1/storelocation?types=R,G,H,N,S&option=&includeOpenAndCloseDates=true&zipCode="+str(zip_code)
        try:
            r = requests.get(location_url,headers=headers).json()
        except:
            continue
        # print("location_url ==== ",r)
        # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
        current_results_len = len(r['Stores'])        # it always need to set total len of record.
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
        page_url = location_url
        
        if "Stores" in r:
            for data in r["Stores"]:
                street_address = data['ADDR']
                hours_of_operation = "Store hours "+ data['STRHOURS']+ ' Pharmacy hours '+data['PHMHOURS']
                
                if len(data['PHONE'])==1 :
                    phone='<MISSING>'
                else:
                    phone  = data['PHONE']
                  
                result_coords.append((data['CLAT'], data['CLON']))
                store = [locator_domain, data['NAME'], data['ADDR'], data['CITY'], data['STATE'], data['ZIP'], country_code,
                        store_number, phone, location_type,  data['CLAT'],  data['CLON'], hours_of_operation.strip(),page_url]

                if store[2] + store[-3] in addresses:
                    continue
                addresses.append(store[2] + store[-3])
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
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
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
