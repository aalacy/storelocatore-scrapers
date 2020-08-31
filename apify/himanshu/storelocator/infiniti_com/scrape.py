import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
from datetime import datetime

session = SgRequests()

session = SgRequests()
from sgrequests import SgRequests
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
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    addresses = []
    base_url= "https://www.infiniti.com/"

    headers = {           
    'Accept': '*/*',
    'apiKey': 'PZUJEgLI2AwEeY3imkqxG2LOgELG3hVd',
    'clientKey': 'lVqTrQx76FnGUhV6AFi7iSy9aXRwLIy7',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
    
    }
    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # print(search.current_zip)
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
    
        json_data = session.get("https://us.nissan-api.net/v2/dealers?size="+str(MAX_RESULTS)+"&lat="+str(lat)+"&long="+str(lng)+"&serviceFilterType=AND&include=openingHours", headers=headers).json()['dealers']
        current_results_len = len(json_data)
        for data in json_data:
            location_name = data['name']    
            street_address = (data['address']['addressLine1'] +" "+ str(data['address']['addressLine2'])).strip()
            # print(street_address)
            city = data['address']['city']
            state = data['address']['stateCode']
            zipp = data['address']['postalCode']
            store_number = data['marketingGroupId']
            phone = data['contact']['phone']
            latitude = data['geolocation']['latitude']
            longitude = data['geolocation']['longitude']
            if 'website' in data['contact']:
                page_url = data['contact']['website']
            else:
                page_url = "<MISSING>"

            hours = data['openingHours']['openingHoursText'].replace("\n"," ").strip()
            
        
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>")
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append(store_number if store_number else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours if hours else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print("data =="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
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
