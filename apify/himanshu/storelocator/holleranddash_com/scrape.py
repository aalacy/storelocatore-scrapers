import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('holleranddash_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 500
    coord = search.next_coord()


    base_url = "https://holleranddash.com"
    while coord:
        result_coords = []
        json_data = session.get("https://maplestreetbiscuits.com/wp-admin/admin-ajax.php?action=store_search&lat="+str(coord[0])+"&lng="+str(coord[1])+"&max_results=100&search_radius=500").json()
        
        for data  in json_data:
        
            location_name = data['store'].split("&#8211;")[0].replace("Order Online!","").strip()
            street_address = (data['address'] +" "+ str(data['address2'])).strip()
            city = data['city']
            state = data['state']
            zipp = data['zip']
            store_number = data['url'].split("=")[-1]
            phone = data['phone']
            lat = data['lat']
            lng = data['lng']
            hours = " ".join(list(bs(data['hours'], "lxml").find("table").stripped_strings))
            page_url = data['url']

            result_coords.append((lat,lng))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city.replace(",",""))
            store.append(state)
            store.append(zipp)   
            store.append("US")
            store.append(store_number.replace('8#index','8').replace('23#index','23'))
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours)
            store.append(page_url)     

            if store[2] in addressess:
                continue
            addressess.append(store[2])

            yield store

        if len(json_data) < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
         


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
