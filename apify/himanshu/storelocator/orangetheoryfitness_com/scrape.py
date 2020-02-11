import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 150
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        base_url=  "https://www.orangetheoryfitness.com/service/directorylisting/filterMarkers?lat="+str(lat)+"&lng="+str(lng)+"&zoom=12"
        
        r = requests.get(base_url)
        
        json_data = r.json()
        current_results_len =len(json_data['markers'])
        for i in json_data['markers']:
            store_number = i['id']
            location_name = i['name']
            street_address = i['address1']
            city = i['city']
            state = i['state']
            zipp = i['zip'].replace("0209","80209").replace("880209","80209").replace("2550","12550").replace("125504","25504").replace("2145","02145").encode('ascii', 'ignore').decode('ascii').strip()
            phone = i['phone'].replace("08837","<MISSING>").replace("(2683)","").encode('ascii', 'ignore').decode('ascii').strip()
            latitude  = i['lat']
            longitude = i['lon']
            page_url = i['web_site']
            result_coords.append((latitude, longitude))
            store = []
            store.append("https://www.orangetheoryfitness.com/")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp)
            store.append("US" if zipp.replace("-",'').replace(" ",'').isdigit() else "CA")
            store.append(store_number if store_number else "<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append("<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            if "Adjuntas" in store :
                pass
            else:
                yield store
            # print("--------------------",store)
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
