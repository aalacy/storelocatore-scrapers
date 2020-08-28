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
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["UK"])
    MAX_RESULTS = 500
    MAX_DISTANCE = 10
    current_results_len = 0  # need to update with no of countc.
    coord = search.next_coord()
    addressess=[]
    headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    returnres=[]
    base_url="https://www.paddypower.com/"
    while coord:
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        result_coords = []
        if coord != None:
            lat = coord[0]
            lng = coord[1]
            data='{"Latitude":"'+str(lat)+'","Longitude":"'+str(lng)+'"}'
            url="https://ppsl.s73.co/api/store/FindStores"
            base_url="https://www.paddypower.com/"
            try:
                r=session.post(url,headers=headers,data=data).json()
            except:
                pass
            for data in r['Payload']:
                location_name=data['StoreName']
                street_address=data['Address1']
                city="<MISSING>"
                state="<MISSING>"
                zipp=data['PostCode']
                StoreNumber =data['StoreNumber']
                phone=data['ContactNumber'].strip()
                latitude=data['Latitude']
                longitude=data['Longitude']
                hour=''
                for h in data['OutputHours']:
                    hour=hour+' '+h['Days']+ ' '+ h['Hours']
                result_coords.append((latitude,longitude))
                store =[]
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp if zipp else "<MISSING>")
                store.append("UK")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hour if hour else "<MISSING>")
                store.append("<MISSING>")
                if store[2] in addressess:
                    continue
                addressess.append(store[2])
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("----------------------",store)
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
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
