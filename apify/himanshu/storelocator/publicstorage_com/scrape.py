import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


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

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
}

return_main_object = []
addresses = []

def store_handler(store_data):
    store = []
    store.append("https://www.publicstorage.com")
    location_request = request_wrapper("https://www.publicstorage.com" + store_data["PLPUrl"],"get",headers=headers)
    if location_request == None:
        return
    location_soup = BeautifulSoup(location_request.text,"lxml")
    name = location_soup.find("h1",{"class":'ps-properties-property-header__header'}).text.strip()
    store.append(name)
    store.append(store_data["Street1"] + " " + store_data["Street2"] if store_data["Street2"] else store_data["Street1"])
    if store[-1] in addresses:
        return
    addresses.append(store[-1])
    store.append(store_data["City"]  if store_data["City"] else "<MISSING>")
    store.append(store_data["StateCode"]  if store_data["StateCode"] else "<MISSING>")
    store.append(store_data["PostalCode"] if store_data["PostalCode"] else "<MISSING>")
    store.append("US")
    store.append(store_data["SiteID"])
    store.append(store_data["PhoneNumber"] if "PhoneNumber" in store_data and store_data["PhoneNumber"] else "<MISSING>")
    store.append("<MISSING>")
    store.append(store_data["Latitude"])
    store.append(store_data["Longitude"])
    hours = ""
    for hour in location_soup.find_all("div",{"class":'ps-properties-property__info__hours__section'}):
        hours = hours + " ".join(list(hour.stripped_strings)) + " "
    store.append(hours if hours != "" else "<MISSING>")
    store.append("https://www.publicstorage.com" + store_data["PLPUrl"])
    return_main_object.append(store)
    #print(len(return_main_object))

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 30
    MAX_DISTANCE = 30
    zip = search.next_zip()
    while zip:
        result_coords = []
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        #print('Pulling Lat-Long %s...' % (str(zip)))
        r_data = '{"location":"' + str(zip) + '"}'
        r_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            "content-type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*"
        }
        r = requests.post("https://www.publicstorage.com/api/sitecore/LocationSearch/RedoSearch",headers=r_headers,data=r_data)
        data = r.json()["Result"]["Units"]
        for store_data in data:
            lat = store_data["Latitude"]
            lng = store_data["Longitude"]
            result_coords.append((lat, lng))
        executor = ThreadPoolExecutor(max_workers=10)
        fs = [ executor.submit(store_handler, store_data) for store_data in data]
        wait(fs)
        executor.shutdown(wait=False)
        if len(data) < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip = search.next_zip()
    for store in return_main_object:
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
