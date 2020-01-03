import csv
import requests
import http.client
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
        MAX_RESULTS = 200
        MAX_DISTANCE = 100
        current_results_len = 0  # need to update with no of count.
        coord = search.next_coord()

        while coord:
            result_coords = []
            lat = coord[0]
            lng = coord[1]
            base_url = "www.gamestop.com"
            conn = http.client.HTTPSConnection("www.gamestop.com")
            location_url = "/on/demandware.store/Sites-gamestop-us-Site/default/Stores-FindStores?radius="+str(MAX_DISTANCE)+"&radius="+str(MAX_DISTANCE)+"&lat="+str(lat)+"&lat="+str(lat)+"&long="+str(lng)+"&long="+str(lng)
            conn.request("GET",location_url)
            res = conn.getresponse()
            data = res.read()
            get_deata = json.loads(data.decode("utf-8"))

            if 'stores' in get_deata:
                current_results_len = len(get_deata['stores'])
                for key,vj in enumerate(get_deata['stores']):
                    locator_domain = base_url
                    location_name = vj['name']
                    street_address = vj['address1']
                    city = vj['city']
                    state = vj['stateCode']
                    zip =  vj['postalCode']
                    store_number = vj['ID']
                    country_code = vj['countryCode']
                    phone = vj['phone']
                    location_type = 'gamestop'
                    latitude = vj['latitude']
                    longitude = vj['longitude']

                    if street_address in addresses:
                        continue
                    addresses.append(street_address)
                    hours_of_operation = vj['storeHours']
                    store = []
                    result_coords.append((latitude, longitude))
                    store.append(locator_domain if locator_domain else '<MISSING>')
                    store.append(location_name if location_name else '<MISSING>')
                    store.append(street_address if street_address else '<MISSING>')
                    store.append(city if city else '<MISSING>')
                    store.append(state if state else '<MISSING>')
                    store.append(zip if zip else '<MISSING>')
                    store.append(country_code if country_code else '<MISSING>')
                    store.append(store_number if store_number else '<MISSING>')
                    store.append(phone if phone else '<MISSING>')
                    store.append(location_type if location_type else '<MISSING>')
                    store.append(latitude if latitude else '<MISSING>')
                    store.append(longitude if longitude else '<MISSING>')
                    store.append('<MISSING>')
                    store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                    store.append('<MISSING>')
                    # print("====",str(store))
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
