# coding=UTF-8
import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None
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
    MAX_RESULTS = 600
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type':'application/json',
    }
    base_url = "https://www.walgreens.com"
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        data='{"r":"50","lat":'+str(lat)+',"lng":'+str(lng)+',"requestType":"dotcom","s":"50","p":1,"q":"'+str(search.current_zip)+'"}'
        location_url = "https://www.walgreens.com/locator/v1/stores/search"
        r = request_wrapper(location_url,'post' ,headers=headers, data=data)
        json_data = r.json()
        current_results_len = len(json_data) 
        if "results"  in json_data:
            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            hours_of_operation = ""
            for location in json_data["results"]:
                try:
                    page_url = "https://www.walgreens.com"+location['storeSeoUrl']
                    r1 = request_wrapper(page_url,'get' ,headers=headers)
                    soup = BeautifulSoup(r1.text,"lxml")
                    hours_of_operation = (soup.find("div",{"class":'service-section'}).find("li",{"class":'single-hours-lists'}).text.replace("day","day ").replace("Fri",'Fri ').replace("Sun","Sun ").replace("Sat","Sat ").replace("pm","pm "))
                except:
                    pass
                storeNumber = location['store']['storeNumber']
                location_name = "Walgreens - Store #"+str(storeNumber)
                phone =location['store']['phone']['areaCode'] + ' '+ location['store']['phone']['number']
                storeNumber = location['storeNumber']
                latitude = location['latitude']
                longitude = location['longitude']
                zipp = location['store']['address']['zip']
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"
                if phone.strip().lstrip():
                    phone = phone
                else:
                    phone = "<MISSING>"  
                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, location['store']['address']['street'].capitalize(), location['store']['address']['city'].capitalize(), location['store']['address']['state'], zipp, country_code,
                        storeNumber, phone.strip(), location_type, latitude, longitude, hours_of_operation,page_url]
                if str(store[2]) + str(store[-3]) not in addresses:
                    addresses.append(str(store[2]) + str(store[-3]))
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
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
