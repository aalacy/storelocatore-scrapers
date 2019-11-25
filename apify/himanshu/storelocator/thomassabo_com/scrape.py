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
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    base_url ="https://www.thomassabo.com"
    while coord:
        # lat = coord[0]
        # lng = coord[1]
        result_coords =[]
        # print(coord)
        url ="https://www.thomassabo.com/on/demandware.store/Sites-TS_INT-Site/en/Shopfinder-GetStores?searchMode=radius"+str(MAX_DISTANCE)+"&searchPhrase=10009&searchDistance=50&lat="+str(coord[0])+"&lng="+str(coord[1])+"&filterBy="
        try:
            r = requests.get(url).json()
        except:
            continue
        
        current_results_len = len(r)
        for loc in r:
            #print(loc)
            if "address1" in loc and "stateCode" in loc:
                zip=''
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(loc['postalCode']))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(loc['postalCode']))

                if ca_zip_list:
                    zip = ca_zip_list[0]
                    country = "CA"
                elif us_zip_list:
                    zip = us_zip_list[0]
                    country = "US"
                else:
                    continue

                name=loc['name'].strip()
                address=loc['address1'].strip()
                city=loc['city'].strip()
                state=loc['stateCode']
             
                phone=''
                if "phone" in loc:
                    phone=loc['phone'].strip()

                storeno=loc['ID'].strip()
                lat=loc['latitude']
                lng=loc['longitude']
                hour = ''
                store=[]
                latitude =lat
                longitude = lng
                result_coords.append((latitude, longitude))
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
                store.append(hour if hour.strip() else "<MISSING>")
                store.append("<MISSING>")
                if store[2]  in addresses:
                    continue
                addresses.append(store[2])
                yield store
                # print("data===="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

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
