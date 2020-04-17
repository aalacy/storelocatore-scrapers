import csv
import requests
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
import sgzip
import json
session = SgRequests()
def write_output(data):
	with open('data.csv', mode='w',newline="") as output_file:
		writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

		# Header
		writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
						 "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
		# Body
		for row in data:
			writer.writerow(row)

def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    returnres=[]
    base_url="https://www.altamed.org/"
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        page_url="https://www.altamed.org/find/resultsJson?type=clinic&affiliates=yes&lat=" + str(lat) +"&lng=" + str(lng)
        r=session.get(page_url).json()
        for item  in r['items']:
            location_name=item['name'].strip()
            addr=item['address'].split(',')
            street_address=addr[0].split('Suite')[0].strip().split('Ste')[0].strip()
            city=addr[-3].strip()
            state=addr[-2].strip()
            zipp=addr[-1].strip()
            phone=item['phone'].strip()
            latitude=item['lat']
            longitude=item['lon']
            location_type = item['location_type']
            hour=re.sub(r'\s+'," ",item['urgent_care_work_hour'].strip()).strip()
            result_coords.append((latitude,longitude))


            store =[]
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hour if hour else "<MISSING>")
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
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
        coord = search.next_coord()
    # return returnres;

def scrape():
    data = fetch_data();
    write_output(data)
scrape()
