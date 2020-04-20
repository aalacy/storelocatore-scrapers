import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
from random import randint
from time import sleep
from datetime import datetime
from sgrequests import SgRequests



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["US","CA"])
    MAX_RESULTS = 50
    MAX_DISTANCE = 100
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    base_url = "https://www.luckybrand.com"
    coord = search.next_coord()
    while coord:
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        
        json_data = session.get("https://liveapi.yext.com/v2/accounts/me/entities/geosearch?api_key=0700165de62eb1a445df7d02b02c7831&v=20181017&location="+str(lat)+",%20"+str(lng)+"&limit=50&radius=500&entityTypes=location,healthcareProfessional,restaurant,healthcareFacility,atm&fields=name,hours,address,websiteUrl&resolvePlaceholders=true&searchIds=").json()['response']['entities']
        current_result_len = len(json_data)
        for data in json_data:
            if "CLOSED" in data['name']:
                continue
            country_code = data['address']['countryCode']
            if country_code not in ['US','CA']:
                continue
            page_url = data['websiteUrl']['url']
            # print(page_url)
            street_address = (data['address']['line1'] +" "+ str(data['address']['line1'])).strip()
            city = data['address']['city']
           
            state = data['address']['region']
            zipp = data['address']['postalCode']
            store_number = data['meta']['id']
            location_type = data['meta']['schemaTypes'][0]
            r = session.get(page_url)
            soup = BeautifulSoup(r.text, "lxml")
            location_name = soup.find("title").text
            try:
                hours = " ".join(list(soup.find("tbody",{"class":"hours-body"}).stripped_strings))
            except:
                hours = "<MISSING>"
            info = json.loads(soup.find(lambda tag:(tag.name == "script") and "latitude" in tag.text).text)
            latitude = info['geo']['latitude']
            longitude = info['geo']['longitude']
            phone = info['telephone']

            result_coords.append((latitude,longitude))
            store = []
            store.append(base_url)            
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
           
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
