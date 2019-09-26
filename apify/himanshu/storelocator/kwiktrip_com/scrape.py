import csv
import requests
from bs4 import BeautifulSoup
import re
# import http.client
import sgzip
import json
import  pprint


def write_output(data):
    with open('kwi.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://www.kwiktrip.com"
    # conn = http.client.HTTPSConnection("guess.radius8.com")
    
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 80
    coords = search.next_coord()
    # search.current_zip """"""""==zip
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5',}
    while coords:
        try:
        # print(coords)
            result_coords = []
            k= requests.get(
                'https://www.kwiktrip.com/locproxy.php?Latitude='+str(coords[0])+'&Longitude='+str(coords[1]) +'&maxDistance='+str(MAX_DISTANCE)+'&limit='+str(MAX_RESULTS),
                headers=headers,
        
            ).json()
        
            # print("response ===", str(r['response']))
            # print(k)
            # data = r['response']
            if "stores" in k:
                for val in k['stores']:
                    # print(val['address'])
                
                    locator_domain = base_url
                    location_name =  val['name']
                    street_address = val['address']['address1']
                    city = val['address']['city']
                    state =  val['address']['state']
                    zip1 =  val['address']['zip']
                    country_code = val['address']['county']
                    store_number = "<MISSING>"
                    phone = val['phone']
                    if 'phone' in val:
                        phone = val['phone']
                    location_type = ''
                    latitude = val['latitude']
                    longitude = val['longitude']
                    if val['open24Hours']:
                        hours_of_operation = "OPEN-24-HOURS"
                    else:
                        hours_of_operation = "<MISSING>"
                        
                    result_coords.append((latitude,longitude))
                    if street_address in addresses:
                        continue
                    addresses.append(street_address)
                    store = []
                    store.append(locator_domain if locator_domain else '<MISSING>')
                    store.append(location_name if location_name else '<MISSING>')
                    store.append(street_address if street_address else '<MISSING>')
                    store.append(city if city else '<MISSING>')
                    store.append(state if state else '<MISSING>')
                    store.append(zip1 if zip1 else '<MISSING>')
                    store.append(country_code if country_code else '<MISSING>')
                    store.append(store_number if store_number else '<MISSING>')
                    store.append(phone if phone else '<MISSING>')
                    store.append(location_type if location_type else '<MISSING>')
                    store.append(latitude if latitude else '<MISSING>')
                    store.append(longitude if longitude else '<MISSING>')
                    store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                    store.append("https://www.kwiktrip.com/locator")
                    # if store[3] in addresses:
                    #     continue
                    # addresses.append(store[3])
                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store
            
            if len(k) < MAX_RESULTS:
                print("max distance update")
                search.max_distance_update(MAX_DISTANCE)
            elif len(k) == MAX_RESULTS:
                print("max count update")
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        except:
            continue
        coords = search.next_coord()
        # break

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
