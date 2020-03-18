import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from datetime import datetime
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

   
    base_url= "https://www.safeway.com/pharmacy.html"

    
    headers = {   
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',        
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
        'accept': 'application/json'
    }
    while zip_code:
        result_coords = []

        location_url = " https://www.safeway.com/abs/pub/storelocator/api/accounts/me/locations/geosearch?api_key=843b2f10cedf121969b2e44eab5f15aa&v=20180530&location="+str(zip_code)+"&limit=10&radius=200&filters=%5B%7B%22custom95965%22%3A%20%7B%22equalTo%22%3A%5B%22safeway%22%5D%7D%7D%5D"
        
        r = session.get(location_url).json()
        current_results_len = len(r['response']['locations'])

        for i in r['response']['locations']:

            street_address = i['address']
            city = i['city']
            state = i['state']
            zipp = i['zip']
            location_type = "Pharmacy "
            phone = i['phone']
            country_code = i['countryCode']
            latitude = i['yextDisplayLat']
            longitude = i['yextDisplayLng']	
            page_url = "https://local.pharmacy.safeway.com/"+str(state.lower())+"/"+str(city.lower().replace(" ","-"))+"/"+str(street_address.lower().replace(" ","-").replace("#","-"))+".html"
            r1 = session.get(page_url)
            soup1 = BeautifulSoup(r1.text, "lxml")
            if soup1.find("h1",{"class":"ContentBanner-h1"}):
                location_name = soup1.find("h1",{"class":"ContentBanner-h1"}).text

                hours_of_operation = " ".join(list(soup1.find("table",{"class":"c-hours-details"}).stripped_strings)).replace("Day of the Week Hours","").strip()
            else:
                location_name = "<MISSING>"
                hours_of_operation = "<MISSING>"
            
        
            result_coords.append((latitude, longitude))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append("<MISSING>")
            store.append(phone )
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            #print("data =="+str(store))
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
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
