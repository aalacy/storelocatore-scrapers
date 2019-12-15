# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import http.client
http.client._MAXHEADERS = 1000


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        
    }

    base_url = "https://www.chevronwithtechron.ca/"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        location_url = "https://www.chevronwithtechron.com/webservices/ws_getChevronTexacoNearMe_r2.aspx?lat="+str(lat)+"&lng="+str(lng)+"&oLat="+str(lat)+"&oLng="+str(lng)+"&brand=chevronTexaco&radius=35"
        try:
            r = requests.get(location_url, headers=headers)
        except:
            continue
        json_data = r.json()
        current_results_len = len(json_data['stations'])
        for i in json_data['stations']:
            location_name = i['name']
            street_address = i['address']
            city = i['city']
            state = i['state']
            zipp = i['zip']
            store_number = i['id']
            phone = i['phone'].replace('.','')
            latitude = i['lat']
            longitude = i['lng']
            href = "https://www.chevronwithtechron.com/station/"+str(street_address.replace(' ','-').replace('.',''))+"-"+str(city.replace(' ','-'))+"-"+str(state)+"-"+str(zipp)+"-id"+str(store_number)
        
            store = []
            result_coords.append((latitude, longitude))
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)   
            store.append("US")
            store.append(store_number)
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append("<MISSING>")
            store.append(href)
            if store[2] in addresses:
                continue     
            addresses.append(store[2])
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
