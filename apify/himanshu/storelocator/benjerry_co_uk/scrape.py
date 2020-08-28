import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
import sgzip
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
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
    search.initialize(country_codes=['gb'])
    MAX_RESULTS = 200
    MAX_DISTANCE = 50
    zip_code = search.next_zip()
    current_result_length = 0
    base_url = "https://www.benjerry.co.uk/"

    while zip_code:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        url = "https://www.benjerry.co.uk/home/scoop-shops/main/scoopshopcontent/genericContent/brand-redesign-header-grid/columnOne/scoop-shop--header.where2GetItActionNew.do"

        payload = 'addressline='+str(zip_code)+'&icons=SHOP%2Cdefault%2CCINEMA'
        headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded',
        }

        json_data = session.post(url, headers=headers, data =  payload).json()
        # print(json_data)
        if "collection" in json_data['response']:
            
            if type(json_data['response']['collection']['poi']) == list:
                current_result_length = len(json_data['response']['collection']['poi'])
                for data in json_data['response']['collection']['poi']:

                    location_name = data['name']
                    street_address = data['address1']

                    if data['address2']:
                        street_address += " " + data['address2']
                    city = data['city']
                    state = json_data['response']['collection']['province']
                    zipp = data['postalcode']
                    location_type = data['icon']
                    phone = data['phone']
                    if data['country'] != "UK":
                        continue
                    country_code = data['country']
                    lat = data['latitude']
                    lng = data['longitude']

                    hours = ''
                    if data['monday']:
                        hours += "Monday" + " " + data['monday']
                    else:
                        hours += "Monday Closed"

                    if data['tuesday']:
                        hours += " " + "Tuesday" + " " + data['tuesday']
                    else:
                        hours += " " + "Tuesday Closed"

                    if data['wednesday']:
                        hours += " " + "Wednesday" + " " + data['wednesday']
                    else:
                        hours += " " + "Wednesday Closed"

                    if data['thursday']:
                        hours += " " + "Thursday" + " " + data['thursday']
                    else:
                        hours += " " + "Thursday Closed"

                    if data['friday']:
                        hours += " " + "Friday" + " " + data['friday']
                    else:
                        hours += " " + "Friday Closed"

                    if data['saturday']:
                        hours += " " + "Saturday" + " " + data['saturday']
                    else:
                        hours += " " + "Saturday Closed"
                    
                    if data['sunday']:
                        hours += " " + "Sunday" + " " + data['sunday']
                    else:
                        hours += " " + "Sunday Closed"

                    if hours.count("Closed") == 7:
                        hours = "<MISSING>"      
                    if data['subdomain']:
                        page_url = "https://www.benjerry.co.uk/"+ str(data['subdomain'])
                    else:
                        page_url = "<MISSING>"
            
                    result_coords.append((lat,lng))
                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)   
                    store.append(country_code)
                    store.append("<MISSING>")
                    store.append(phone)
                    store.append(location_type)
                    store.append(lat)
                    store.append(lng)
                    store.append(hours)
                    store.append(page_url)     
                
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    if store[2] + store[1] in addresses:
                        continue
                    addresses.append(store[2] + store[1])
                    yield store
            else:
                current_result_length = 1
                data = json_data['response']['collection']['poi']

                location_name = data['name']
                street_address = data['address1']

                if data['address2']:
                    street_address += " " + data['address2']
                city = data['city']
                state = json_data['response']['collection']['province']
                zipp = data['postalcode']
                location_type = data['icon']
                phone = data['phone']
                country_code = data['country']
                lat = data['latitude']
                lng = data['longitude']

                hours = ''
                if data['monday']:
                    hours += "Monday" + " " + data['monday']
                else:
                    hours += "Monday Closed"

                if data['tuesday']:
                    hours += " " + "Tuesday" + " " + data['tuesday']
                else:
                    hours += " " + "Tuesday Closed"

                if data['wednesday']:
                    hours += " " + "Wednesday" + " " + data['wednesday']
                else:
                    hours += " " + "Wednesday Closed"

                if data['thursday']:
                    hours += " " + "Thursday" + " " + data['thursday']
                else:
                    hours += " " + "Thursday Closed"

                if data['friday']:
                    hours += " " + "Friday" + " " + data['friday']
                else:
                    hours += " " + "Friday Closed"

                if data['saturday']:
                    hours += " " + "Saturday" + " " + data['saturday']
                else:
                    hours += " " + "Saturday Closed"
                
                if data['sunday']:
                    hours += " " + "Sunday" + " " + data['sunday']
                else:
                    hours += " " + "Sunday Closed"

                if hours.count("Closed") == 7:
                    hours = "<MISSING>"      
                if data['subdomain']:
                    page_url = "https://www.benjerry.co.uk/"+ str(data['subdomain'])
                else:
                    page_url = "<MISSING>"
        
                result_coords.append((lat,lng))
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)   
                store.append(country_code)
                store.append("<MISSING>")
                store.append(phone)
                store.append(location_type)
                store.append(lat)
                store.append(lng)
                store.append(hours)
                store.append(page_url)     
            
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if store[2] + store[1] not in addresses:
                    yield store
                addresses.append(store[2] + store[1])
                
        else:
            pass
        # print(current_result_length)
        if current_result_length < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_result_length == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
